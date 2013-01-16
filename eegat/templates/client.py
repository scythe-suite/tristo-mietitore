#!/usr/bin/env python

import sys
# {% if not config.DEBUG %}
sys.excepthook = lambda t, v, tb: sys.exit( 'An unexpected error occurred!' )
# {% endif %}

from base64 import encodestring, decodestring
from io import BytesIO
from os import walk, stat
from os.path import join, abspath, isdir, expanduser, expandvars
from re import compile as recompile
from tarfile import TarFile
from urllib import urlencode
from urllib2 import urlopen

DATA = '{{ data }}'
SIGNATURE = '{{ signature }}'
BASE_URL = '{{ request.url_root }}'
EEG_HOME = expandvars( expanduser( '{{ config.EEG_HOME }}' ) )
ENVIRONMENT_SETUP = """{{ config.ENVIRONMENT_SETUP }}"""

MAX_FILESIZE = 10 * 1024
MAX_NUM_FILES = 1024

def tar( dir = '.', glob = '.*', verbose = True ):
	if not isdir( dir ): raise ValueError( '{0} is not a directory'.format( dir ) )
	dir = abspath( dir )
	glob = recompile( glob )
	buf = BytesIO()
	tf = TarFile.open( mode = 'w', fileobj = buf )
	offset = len( dir ) + 1
	num_files = 0
	for base, dirs, files in walk( dir, followlinks = True ):
		if num_files > MAX_NUM_FILES: break
		for fpath in files:
			path = join( base, fpath )
			rpath = path[ offset: ]
			if glob.search( rpath ) and stat( path ).st_size < MAX_FILESIZE:
				num_files += 1
				if num_files > MAX_NUM_FILES: break
				if verbose: sys.stderr.write( rpath + '\n' )
				with open( path, 'r' ) as f:
					ti = tf.gettarinfo( arcname = rpath, fileobj = f )
					tf.addfile( ti, fileobj = f )
	tf.close()
	return encodestring( buf.getvalue() )

def untar( data, dir = '.' ):
	f = BytesIO( decodestring( data ) )
	tf = TarFile.open( mode = 'r', fileobj = f )
	tf.extractall( dir )
	tf.close()

def upload_tar( glob = '.*', dir = '.' ):
	conn = urlopen( BASE_URL, urlencode( {
		'signature': SIGNATURE,
		'tar': tar( join( EEG_HOME, dir ), glob, False )
	} ) )
	ret = conn.read()
	conn.close()
	return ret

def download_tar():
	conn = urlopen( BASE_URL, urlencode( { 'signature': SIGNATURE } ) )
	untar( conn.read(), EEG_HOME )
	conn.close()
	return ''

def setenv():
	profile = expanduser( '~/.bash_profile' )
	comment = '# EEG environment setup'
	to_append = comment + ENVIRONMENT_SETUP.format( EEG_HOME )
	with open( profile, 'r' ) as f: tmp = f.read()
	if tmp.find( comment ) !=  -1: return 'bash profile already modified'
	with open( profile, 'a' ) as f: f.write( '\n' + to_append + '\n' )
	return ''

if __name__ == '__main__':
	try:
		_, verb = sys.argv.pop( 0 ), sys.argv.pop( 0 )
		dispatch = {
			'_t': tar,
			'se': setenv,
			'ul': upload_tar,
			'dl': download_tar,
			'id': lambda *args: ', '.join( [ SIGNATURE.split( ':' )[ 0 ], DATA ] )
		}
		res = dispatch[ verb ]( *sys.argv )
		if res: print res
	except KeyError:
		sys.exit( 'wrong verb' )
	except IndexError:
		sys.exit( 'wrong number of args' )
