from base64 import encodestring, decodestring
from hmac import new as mac
from hashlib import sha256
from os import makedirs
from os.path import join, isdir
from tarfile import TarFile
from time import time

from flask import Flask, render_template, request

app = Flask( __name__ )
app.config.from_envvar( 'EEGNG_SETTINGS' )
_ru = app.config[ 'REGISTERED_UIDS' ]
_rus = {}
for l in _ru.splitlines():
	if not l: continue
	uid, data = l.strip().split( '\t' )
	_rus[ uid ] = data
app.config[ 'REGISTERED_UIDS' ] = _rus

def sign( uid ):
	return '{0}:{1}'.format( uid, mac( app.config[ 'SECRET_KEY' ], uid, sha256 ).hexdigest() )

def check( signature ):
	try:
		uid, check = signature.split( ':' )
	except ValueError:
		return False
	return sign( uid ) == signature

@app.route( '/<uid>' )
def bootstrap( uid ):
	try:
		data = app.config[ 'REGISTERED_UIDS' ][ uid ]
		client = encodestring( render_template( 'client.py', data = data, signature = sign( uid ) ) )
		status = 200
	except KeyError:
		client = ''
		status = 200
	return render_template( 'bootstrap.py', client = client ), status, { 'Content-Type': 'text/plain' }

@app.route( '/', methods = [ 'POST' ] )
def handle():
	allowed = False
	try:
		signature = request.form[ 'signature' ]
		allowed = check( signature )
		uid, _ = signature.split( ':' )
	except KeyError:
		pass
	if not allowed: return 'print "Invalid or absent signature"', 401, { 'Content-Type': 'text/plain' }
	if 'tar' in request.form:
		data = decodestring( request.form[ 'tar' ] )
		dest_dir = join( app.config[ 'UPLOAD_DIR' ], uid )
		if not isdir( dest_dir ): makedirs( dest_dir )
		dest = join( dest_dir, str( int( time() * 1000 ) ) + '.tar' )
		with open( dest, 'w' ) as f:
			f.write( data )
		tf = TarFile.open( dest, mode = 'r' )
		names = tf.getnames()
		tf.close()
		return '\n'.join( names ), 200, { 'Content-Type': 'text/plain' }
	else:
		return app.config[ 'BUNDLE' ], 200, { 'Content-Type': 'text/plain' }

if __name__ == '__main__':
	app.run( port = 8000 )
