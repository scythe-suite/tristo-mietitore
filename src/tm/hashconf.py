from argparse import ArgumentParser
from base64 import decodebytes
from hashlib import sha256
from hmac import new as newmac
from io import BytesIO
from operator import attrgetter
from tarfile import TarFile


def hashtar(secret, data):
    mac = newmac(secret.encode('utf-8'), digestmod=sha256)
    f = BytesIO(decodebytes(data.encode('utf-8')))
    with TarFile.open(mode="r", fileobj=f) as tf:
        members = tf.getmembers()
        files = [m for m in members if m.isfile()]
        files.sort(key=attrgetter("name"))
        for f in files:
            mac.update(f.tobuf())
    return mac.hexdigest()


def main():

    parser = ArgumentParser(prog="tm hashconf")
    parser.add_argument("conf_file", help="The configuration file")

    args = parser.parse_args()

    conf_file = {}
    with open(args.conf_file, "r") as inf:
        exec(inf, conf_file)
    print(hashtar(conf_file["SECRET_KEY"], conf_file["TAR_DATA"]))


if __name__ == "__main__":
    main()
