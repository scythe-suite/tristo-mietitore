#!/usr/bin/env python

import sys
sys.excepthook = lambda t, v, tb: sys.exit( format_exception_only( t, v )[ -1 ].strip() )

from base64 import encodestring, decodestring
from fnmatch import fnmatch
from io import BytesIO
from os import walk, stat
from os.path import join, abspath, isdir, expanduser
from tarfile import TarFile
from traceback import format_exception_only
from urllib import urlencode
from urllib2 import urlopen

SIGNATURE = '{{ signature }}'
BASE_URL = '{{ base_url }}'
DOWNLOAD_DIR = expanduser( '{{ download_dir }}' )
DATA = '{{ data }}'

MAX_FILESIZE = 10 * 1024
MAX_NUM_FILES = 1024

def tar( dir, glob = '*', verbose = True ):
	if not isdir( dir ): raise ValueError( '{0} is not a directory'.format( dir ) )
	dir = abspath( dir )
	buf = BytesIO()
	tf = TarFile.open( mode = 'w', fileobj = buf )
	offset = len( dir ) + 1
	num_files = 0
	for base, dirs, files in walk( dir ):
		if num_files > MAX_NUM_FILES: break
		for fpath in files:
			path = join( base, fpath )
			if fnmatch( path, glob ) and stat( path ).st_size < MAX_FILESIZE:
				num_files += 1
				if num_files > MAX_NUM_FILES: break
				if verbose: sys.stderr.write( path + '\n' )
				with open( path, 'r' ) as f:
					ti = tf.gettarinfo( arcname = path[ offset: ], fileobj = f )
					tf.addfile( ti, fileobj = f )
	tf.close()
	return encodestring( buf.getvalue() )

def untar( data, dir = '.' ):
	f = BytesIO( decodestring( data ) )
	tf = TarFile.open( mode = 'r', fileobj = f )
	tf.extractall( dir )
	tf.close()
	return ''

def upload( data ):
	conn = urlopen( BASE_URL, urlencode( { 'signature': SIGNATURE, 'data': data } ) )
	ret = conn.read()
	conn.close()
	return ret

def download():
	conn = urlopen( BASE_URL, urlencode( { 'signature': SIGNATURE } ) )
	ret = conn.read()
	conn.close()
	return ret

def update():
	uid, _ = SIGNATURE.split( ':' )
	conn = urlopen( BASE_URL + uid )
	ret = conn.read()
	conn.close()
	exec compile( ret, '<string>', 'exec' )
	return ''

if __name__ == '__main__':
	try:
		_, verb = sys.argv.pop( 0 ), sys.argv.pop( 0 )
		dispatch = {
			'_t': tar,
			'_u': update,
			'ul': lambda *args: upload( tar( *args, verbose = False ) ),
			'dl': lambda *args: untar( download(), DOWNLOAD_DIR ),
			'id': lambda *args: DATA
		}
		res = dispatch[ verb ]( *sys.argv )
		if res: print res
	except KeyError:
		sys.exit( 'wrong verb' )
	except IndexError:
		sys.exit( 'wrong number of args' )

