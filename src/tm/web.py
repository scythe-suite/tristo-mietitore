from base64 import decodestring, encodestring
from codecs import BOM_UTF8
from errno import EEXIST
from hashlib import sha256
from hmac import new as mac
from logging import INFO, FileHandler, Formatter, StreamHandler, getLogger
from os import O_CREAT, O_EXCL, O_WRONLY, close, environ, getpid, makedirs
from os import open as os_open
from os import write
from os.path import abspath, expanduser, expandvars, isdir, join
from sys import argv, exit
from tarfile import TarFile
from time import time

from jinja2 import PackageLoader

from flask import Flask, render_template, request
from tm.hashconf import hashtar
from tm.zipgettext import translation


def safe_makedirs(path):
    try:
        makedirs(path, 0o700)
    except OSError as e:
        if e.errno == EEXIST and isdir(path):
            pass
        else:
            raise RuntimeError("{0} exists and is not a directory".format(path))


# get confs
app = Flask(__name__)
try:
    app.config.from_envvar("TM_SETTINGS")
except:
    exit("Error loading TM_SETTINGS, is such variable defined?")

# setup the loader so that if finds the templates also in the zip file
app.jinja_loader = PackageLoader("tm", "client")

# setup the endpoint
if not "BASE_URL" in app.config:
    app.config["BASE_URL"] = None

# make UPLOAD_DIR resolved and absolute
app.config["UPLOAD_DIR"] = abspath(expandvars(expanduser(app.config["UPLOAD_DIR"])))
safe_makedirs(app.config["UPLOAD_DIR"])

# compute a digest of TAR_DATA to show at root URL
app.config["TAR_DIGEST"] = hashtar(app.config["SECRET_KEY"], app.config["TAR_DATA"])

# setup logging
if not app.debug:
    sh = StreamHandler()
    sh.setLevel(INFO)
    f = Formatter(
        "%(asctime)s [%(process)s] [%(levelname)s] Flask: %(name)s [in %(pathname)s:%(lineno)d] %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )
    sh.setFormatter(f)
    app.logger.addHandler(sh)
    app.logger.setLevel(INFO)
EVENTS_LOG = getLogger("EVENTS_LOG")
EVENTS_LOG.setLevel(INFO)
fh = FileHandler(join(app.config["UPLOAD_DIR"], "EVENTS-{}.log".format(getpid())))
fh.setLevel(INFO)
f = Formatter("%(asctime)s: %(message)s", "%Y-%m-%d %H:%M:%S")
fh.setFormatter(f)
EVENTS_LOG.addHandler(fh)
EVENTS_LOG.info("Start")

# setup translation
translations = translation(app.config["LANG"])
_ = translations.gettext
app.jinja_env.add_extension("jinja2.ext.i18n")
app.jinja_env.install_gettext_translations(translations)


def _sign(uid):
    return "{0}:{1}".format(uid, mac(app.config["SECRET_KEY"], uid, sha256).hexdigest())


def _as_text(msg="", code=200, headers={"Content-Type": "text/plain;charset=UTF-8"}):
    return msg, code, headers


# if called with a registered UID, the first time it's called returns ( info,
# signature ),then ( info, None ); if called with an unkniwn UID returns
# ( None, None ) -- uses filesystem locking to be thread safe
def sign(uid):
    try:
        info = app.config["REGISTERED_UIDS"][uid]
    except KeyError:
        return None, None  # not registered
    dest_dir = join(app.config["UPLOAD_DIR"], uid)
    safe_makedirs(dest_dir)
    try:
        fd = os_open(
            join(dest_dir, "SIGNATURE.tsv"), O_CREAT | O_EXCL | O_WRONLY, 0o600
        )
    except OSError as e:
        if e.errno == EEXIST:
            return info, None  # already signed
        else:
            raise
    else:
        signature = _sign(uid)
        write(
            fd, "{0}\t{1}\t{2}\n".format(uid, info, request.remote_addr).encode("utf8")
        )
        close(fd)
    return info, signature


# returns None if the signature is malformed, or invalid
def extract_uid(signature):
    try:
        uid, check = signature.split(":")
    except ValueError:
        return None
    else:
        return uid if _sign(uid) == signature else None


@app.route("/<uid>")
def bootstrap(uid):
    try:
        info, signature = sign(uid)
        client_code = (
            encodestring(
                render_template(
                    "__init__.py",
                    info=info,
                    signature=signature,
                    base_url=app.config["BASE_URL"],
                ).encode("utf8")
            )
            if signature
            else None
        )
        if signature:
            EVENTS_LOG.info("Signed: {0}@{1}".format(uid, request.remote_addr))
        elif info:
            EVENTS_LOG.info(
                "Not signed (already done): {0}@{1}".format(uid, request.remote_addr)
            )
        else:
            EVENTS_LOG.info(
                "Not signed (not registered): {0}@{1}".format(uid, request.remote_addr)
            )
        return _as_text(
            render_template(
                "bootstrap.py",
                client_code=client_code,
                info=info,
                base_url=app.config["BASE_URL"],
            )
        )
    except:
        if app.debug:
            raise
        else:
            app.logger.exception("")
            return _as_text(
                BOM_UTF8
                + "print 'echo \"{0}\"'\n".format(
                    _("An unexpected bootstrap error occurred!")
                )
            )


@app.route("/", methods=["GET", "POST"])
def handle():
    try:
        if request.method == "GET":
            return _as_text(app.config["TAR_DIGEST"])
        try:
            signature = request.form["signature"]
        except KeyError:
            uid = None
        else:
            uid = extract_uid(signature)
        if not uid:
            EVENTS_LOG.info("Unauthorized: {0}@{1}".format(uid, request.remote_addr))
            return _as_text("# {0}\n".format(_("Invalid or absent signature!")), 401)
        if "tar" in request.form:  # this is an upload
            data = decodestring(request.form["tar"])
            dest = join(app.config["UPLOAD_DIR"], uid, str(int(time() * 1000)) + ".tar")
            with open(dest, "w") as f:
                f.write(data)
            tf = TarFile.open(dest, mode="r")
            names = tf.getnames()
            tf.close()
            EVENTS_LOG.info("Upload: {0}@{1}".format(uid, request.remote_addr))
            return _as_text("\n".join(sorted(names)))
        else:  # this is a download
            EVENTS_LOG.info("Download: {0}@{1}".format(uid, request.remote_addr))
            return _as_text(app.config["TAR_DATA"])
    except:
        if app.debug:
            raise
        else:
            app.logger.exception("")
            return _as_text(
                "# {0}\n".format(_("An unexpected server error occurred!")), 500
            )


def main():
    try:
        import eventlet
        from eventlet import wsgi

        EVENTS_LOG.info("Using eventlet...")
        wsgi.server(eventlet.listen(("0.0.0.0", int(environ.get("PORT", 8000)))), app)
    except ImportError:
        app.run(
            host="0.0.0.0", port=int(environ.get("PORT", 8000)), debug=len(argv) > 1
        )


if __name__ == "__main__":
    main()

