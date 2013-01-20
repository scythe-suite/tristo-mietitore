from base64 import encodestring, decodestring
from codecs import BOM_UTF8
from errno import EEXIST
from gettext import translation
from hmac import new as mac
from hashlib import sha256
from logging import StreamHandler, FileHandler, Formatter, INFO, getLogger
from os import makedirs, open as os_open, close, write, O_EXCL, O_CREAT, O_WRONLY
from os.path import join, isdir, abspath, expanduser, expandvars, dirname
from sys import argv, exit
from tarfile import TarFile
from time import time

from flask import Flask, render_template, request

def safe_makedirs( path ):
	try:
		makedirs( path, 0700 )
	except OSError as e:
		if e.errno == EEXIST and isdir( path ): pass
		else: raise RuntimeError( '{0} exists and is not a directory'.format( path ) )

app = Flask( __name__ )
try:
	app.config.from_envvar( 'TM_SETTINGS' )
	app.logger
except:
	exit( 'Error loading TM_SETTINGS, is such variable defined?' )

# make UPLOAD_DIR resolved and absolute
app.config[ 'UPLOAD_DIR' ] = abspath( expandvars( expanduser( app.config[ 'UPLOAD_DIR' ] ) ) )
safe_makedirs( app.config[ 'UPLOAD_DIR' ] )

# setup logging
if not app.debug:
	sh = StreamHandler()
	sh.setLevel( INFO )
	f = Formatter( '%(asctime)s [%(process)s] [%(levelname)s] Flask: %(name)s [in %(pathname)s:%(lineno)d] %(message)s', '%Y-%m-%d %H:%M:%S' )
	sh.setFormatter( f )
	app.logger.addHandler( sh )
	app.logger.setLevel( INFO )

EVENTS_LOG = getLogger( 'EVENTS_LOG' )
EVENTS_LOG.setLevel( INFO )
fh = FileHandler( join( app.config[ 'UPLOAD_DIR' ], 'EVENTS.log' ) )
fh.setLevel( INFO )
f = Formatter( '%(asctime)s: %(message)s', '%Y-%m-%d %H:%M:%S' )
fh.setFormatter( f )
EVENTS_LOG.addHandler( fh )

EVENTS_LOG.info( 'Start' )

# setup translation
translations = translation( 'tm', join( dirname( __file__ ), 'locale' ), languages = [ app.config[ 'LANG' ] ], fallback = True )
_ = translations.gettext
app.jinja_env.add_extension( 'jinja2.ext.i18n' )
app.jinja_env.install_gettext_translations( translations )

def _sign( uid ):
	return '{0}:{1}'.format( uid, mac( app.config[ 'SECRET_KEY' ], uid, sha256 ).hexdigest() )

def _as_text( msg = '', code = 200, headers = { 'Content-Type': 'text/plain;charset=UTF-8' } ):
	return msg, code, headers

# if called with a registered UID, the first time it's called returns ( data,
# signature ),then ( data, None ); if called with an unkniwn UID returns
# ( None, None ) -- uses filesystem locking to be thread safe
def sign( uid ):
	try:
		data = app.config[ 'REGISTERED_UIDS' ][ uid ]
	except KeyError:
		return None, None  # not registered
	dest_dir = join( app.config[ 'UPLOAD_DIR' ], uid )
	safe_makedirs( dest_dir )
	try:
		fd = os_open( join( dest_dir, 'SIGNATURE.tsv' ), O_CREAT | O_EXCL | O_WRONLY, 0600 )
	except OSError as e:
		if e.errno == EEXIST: return data, None  # already signed
		else: raise
	else:
		signature = _sign( uid )
		write( fd, u'{0}\t{1}\t{2}\n'.format( uid, data, request.remote_addr ).encode( 'utf8' ) )
		close( fd )
	return data, signature

# returns None if the signature is malformed, or invalid
def extract_uid( signature ):
	try:
		uid, check = signature.split( ':' )
	except ValueError:
		return None
	else:
		return uid if _sign( uid ) == signature else None


@app.route( '/<uid>' )
def bootstrap( uid ):
	try:
		data, signature = sign( uid )
		client = encodestring( render_template( 'client.py', data = data, signature = signature ).encode( 'utf8' ) ) if signature else None
		if signature:
			EVENTS_LOG.info( 'Signed: {0}@{1}'.format( uid, request.remote_addr ) )
		elif data:
			EVENTS_LOG.info( 'Not signed (already done): {0}@{1}'.format( uid, request.remote_addr ) )
		else:
			EVENTS_LOG.info( 'Not signed (not registered): {0}@{1}'.format( uid, request.remote_addr ) )
		return _as_text( render_template( 'bootstrap.py', client = client, data = data ) )
	except:
		if app.debug:
			raise
		else:
			app.logger.exception( '' )
			return _as_text( BOM_UTF8 + 'print \'echo "{0}"\'\n'.format( _( 'An unexpected bootstrap error occurred!' ) ) )

@app.route( '/', methods = [ 'GET', 'POST' ] )
def handle():
	try:
		if request.method == 'GET': return _as_text()
		try:
			signature = request.form[ 'signature' ]
		except KeyError:
			uid = None
		else:
			uid = extract_uid( signature )
		if not uid:
			EVENTS_LOG.info( 'Unauthorized: {0}@{1}'.format( signature, request.remote_addr ) )
			return _as_text( '# {0}\n'.format( _( 'Invalid or absent signature!' ) ), 401 )
		if 'tar' in request.form:  # this is an upload
			data = decodestring( request.form[ 'tar' ] )
			dest = join( app.config[ 'UPLOAD_DIR' ], uid, str( int( time() * 1000 ) ) + '.tar' )
			with open( dest, 'w' ) as f: f.write( data )
			tf = TarFile.open( dest, mode = 'r' )
			names = tf.getnames()
			tf.close()
			EVENTS_LOG.info( 'Upload: {0}@{1}'.format( uid, request.remote_addr ) )
			return _as_text( '\n'.join( names ) )
		else:  # this is a download
			EVENTS_LOG.info( 'Download: {0}@{1}'.format( uid, request.remote_addr ) )
			return _as_text( app.config[ 'TAR_DATA' ] )
	except:
		if app.debug:
			raise
		else:
			app.logger.exception( '' )
			return _as_text( '# {0}\n'.format( _( 'An unexpected server error occurred!' ) ), 500 )

def main():
	app.run( host= '0.0.0.0', port = 8000, debug = len( argv ) == 1 )

if __name__ == '__main__':
	main()
