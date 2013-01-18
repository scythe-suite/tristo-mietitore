#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
# {% if not config.DEBUG %}
sys.excepthook = lambda t, v, tb: sys.exit( '{{ _( "An unexpected client error occurred!" ) }}' )
# {% endif %}

from base64 import encodestring, decodestring
from io import BytesIO
from os import walk, stat
from os.path import join, abspath, isdir
from re import compile as recompile
from tarfile import TarFile
from urllib import urlencode
from urllib2 import urlopen

ENVIRONMENT_SETUP = """{{ config.ENVIRONMENT_SETUP }}"""
BASE_URL = """{{ request.url_root }}"""
TM_HOME = """### tm_home ###"""
SIGNATURE = """{{ signature }}"""

def tar( dir = '.', glob = '.*', verbose = True ):
	MAX_FILESIZE = 10 * 1024
	MAX_NUM_FILES = 1024
	if not isdir( dir ): raise ValueError( '{0} is not a directory'.format( dir ) )
	dir = abspath( dir )
	glob = recompile( glob )
	buf = BytesIO()
	with TarFile.open( mode = 'w', fileobj = buf ) as tf:
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
	return encodestring( buf.getvalue() )

def untar( data, dir = '.' ):
	f = BytesIO( decodestring( data ) )
	with TarFile.open( mode = 'r', fileobj = f ) as tf: tf.extractall( dir )

def upload_tar( glob = '.*', dir = '.' ):
	conn = urlopen( BASE_URL, urlencode( {
		'signature': SIGNATURE,
		'tar': tar( join( TM_HOME, dir ), glob, False )
	} ) )
	ret = conn.read()
	conn.close()
	return ret

def download_tar():
	conn = urlopen( BASE_URL, urlencode( { 'signature': SIGNATURE } ) )
	untar( conn.read(), TM_HOME )
	conn.close()
	return ''

if __name__ == '__main__':
	try:
		_, verb = sys.argv.pop( 0 ), sys.argv.pop( 0 )
		dispatch = {
			'ul': upload_tar,
			'dl': download_tar,
			'id': lambda *args: SIGNATURE.split( ':' )[ 0 ]
		}
		res = dispatch[ verb ]( *sys.argv )
		if res: print res
	except KeyError:
		sys.exit( 'Wrong verb' )
	except IndexError:
		sys.exit( 'Wrong number of args' )
