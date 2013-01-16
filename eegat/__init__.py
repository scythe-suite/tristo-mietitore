from base64 import encodestring, decodestring
from errno import EEXIST
from hmac import new as mac
from hashlib import sha256
from logging import StreamHandler, Formatter, INFO
from os import makedirs, open as os_open, close, write, O_EXCL, O_CREAT, O_WRONLY
from os.path import join, isdir, abspath, expanduser, expandvars
from tarfile import TarFile
from time import time

from flask import Flask, render_template, request

app = Flask( __name__ )
app.config.from_envvar( 'EEGNG_SETTINGS' )
if not app.debug:
	sh = StreamHandler()
	f = Formatter( '%(asctime)s [%(process)s] [%(levelname)s] Flask: %(name)s [in %(pathname)s:%(lineno)d] %(message)s', '%Y-%m-%d %H:%M:%S' )
	sh.setFormatter( f )
	app.logger.addHandler( sh )
	app.logger.setLevel( INFO )
app.config[ 'UPLOAD_DIR' ] = abspath( expandvars( expanduser( app.config[ 'UPLOAD_DIR' ] ) ) )

def _sign( uid ):
	return '{0}:{1}'.format( uid, mac( app.config[ 'SECRET_KEY' ], uid, sha256 ).hexdigest() )

def sign( uid ):
	try:
		dest_dir = join( app.config[ 'UPLOAD_DIR' ], uid )
		try:
			makedirs( dest_dir )
		except OSError as e:
			if e.errno == EEXIST and isdir( dest_dir ): pass
			else: raise RuntimeError( '{0} exists and is not a directory'.format( dest_dir ) )
		fd = os_open( join( dest_dir, 'IP.txt' ), O_CREAT | O_EXCL | O_WRONLY, 0600 )
	except OSError as e:  # already signed
		if e.errno == EEXIST: signature = None
		else: raise
	else:
		signature = _sign( uid )
		write( fd, request.remote_addr + '\n' )
		close( fd )
	return signature

def check( signature ):
	try:
		uid, check = signature.split( ':' )
	except ValueError:
		return False
	else:
		return _sign( uid ) == signature

@app.route( '/<uid>' )
def bootstrap( uid ):
	try:
		try:
			data = app.config[ 'REGISTERED_UIDS' ][ uid ]
		except KeyError:
			data = None  # not registered
			client = None
		else:
			signature = sign( uid )
			client = encodestring( render_template( 'client.py', data = data, signature = signature ) ) if signature else None
		return render_template( 'bootstrap.py', client = client, data = data ), 200, { 'Content-Type': 'text/plain' }
	except:
		if app.debug:
			raise
		else:
			app.logger.exception( '' )
			return 'print \'echo "An unexpected error occurred!"\'\n', 200, { 'Content-Type': 'text/plain' }

@app.route( '/', methods = [ 'POST' ] )
def handle():
	try:
		try:
			signature = request.form[ 'signature' ]
		except KeyError:
			allowed = False
		else:
			allowed = check( signature )
			uid = signature.split( ':' )[ 0 ]
		if not allowed: return '# Invalid or absent signature!\n', 401, { 'Content-Type': 'text/plain' }
		if 'tar' in request.form:  # this is an upload
			data = decodestring( request.form[ 'tar' ] )
			dest = join( app.config[ 'UPLOAD_DIR' ], uid, str( int( time() * 1000 ) ) + '.tar' )
			with open( dest, 'w' ) as f: f.write( data )
			tf = TarFile.open( dest, mode = 'r' )
			names = tf.getnames()
			tf.close()
			return '\n'.join( names ), 200, { 'Content-Type': 'text/plain' }
		else:  # this is a download
			return app.config[ 'DOWNLOAD_BUNDLE' ], 200, { 'Content-Type': 'text/plain' }
	except:
		if app.debug:
			raise
		else:
			app.logger.exception( '' )
			return '# An unexpected error occurred!"\n', 500, { 'Content-Type': 'text/plain' }

if __name__ == '__main__':
	app.run( port = 8000, debug = True )
