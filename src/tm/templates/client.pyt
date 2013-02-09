#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
# {% if not config.DEBUG %}
if __name__ == '__main__':
	sys.excepthook = lambda t, v, tb: sys.exit( '{{ _( "An unexpected client error occurred!" ) }}' )
# {% endif %}

from base64 import encodestring, decodestring
from io import BytesIO
from operator import attrgetter
from os import walk, stat, chmod, makedirs, mkdir
from os.path import join, abspath, isdir, dirname, exists
from re import compile as recompile
from tarfile import TarFile
from urllib import urlencode
from urllib2 import urlopen

ENVIRONMENT_SETUP = """{{ config.ENVIRONMENT_SETUP }}"""
BASE_URL = """{{ request.url_root }}"""
HOME = """### home ###"""
SIGNATURE = """{{ signature }}"""
INFO = """{{ info }}"""

def tar( dir = '.', glob = '.*', verbose = True ):
	MAX_FILESIZE = 10 * 1024
	MAX_NUM_FILES = 1024
	if not isdir( dir ): raise ValueError( '{0} is not a directory'.format( dir ) )
	dir = abspath( dir )
	offset = len( dir ) + 1
	glob = recompile( glob )
	buf = BytesIO()
	with TarFile.open( mode = 'w', fileobj = buf, dereference = True ) as tf:
		num_files = 0
		nonempty_dirs = set()
		for base, dirs, files in walk( dir, followlinks = True ):
			if num_files > MAX_NUM_FILES: break
			for fpath in files:
				path = join( base, fpath )
				rpath = path[ offset: ]
				if glob.search( rpath ) and stat( path ).st_size < MAX_FILESIZE:
					num_files += 1
					if num_files > MAX_NUM_FILES: break
					if verbose: sys.stderr.write( rpath + '\n' )
					with open( path, 'rb' ) as f:
						ti = tf.gettarinfo( arcname = rpath, fileobj = f )
						ti.mtime = 1
						nonempty_dirs.add( dirname( path ) )
						tf.addfile( ti, fileobj = f )
		for path in nonempty_dirs:
			rpath = path[ offset: ]
			if not rpath: continue
			ti = tf.gettarinfo( name = path, arcname = rpath )
			ti.mtime = 1
			tf.addfile( ti )
	return encodestring( buf.getvalue() )

def lstar( data, verbose = True ):
	f = BytesIO( decodestring( data ) )
	with TarFile.open( mode = 'r', fileobj = f ) as tf: tf.list( verbose )

def untar( data, dir = '.' ):
	if not exists( dir ):
		makedirs( dir, 0700 )
	else:
		chmod( dir, 0700 )
	f = BytesIO( decodestring( data ) )
	with TarFile.open( mode = 'r', fileobj = f ) as tf:
		members = tf.getmembers()
		dirs = []
		files = []
		for m in members:
			if m.isdir(): dirs.append( m )
			if m.isfile(): files.append( m )
		dirs.sort( key = attrgetter( 'name' ) )
		for d in dirs:
			dp = join( dir, d.name )
			if not exists( dp ): mkdir( dp, 0700 )
			else: chmod( dp, 0700 )
		for f in files:
			fp = join( dir, f.name )
			if exists( fp ): chmod( fp, 0700 )
			tf.extract( f, dir )
		dirs.reverse()
		for d in dirs:
			tf.extract( d, dir )

def upload_tar( glob = '.*', dir = '.' ):
	conn = urlopen( BASE_URL, urlencode( {
		'signature': SIGNATURE,
		'tar': tar( join( HOME, dir ), glob, False )
	} ) )
	ret = conn.read()
	conn.close()
	return ret

def download_tar():
	conn = urlopen( BASE_URL, urlencode( { 'signature': SIGNATURE } ) )
	untar( conn.read(), HOME )
	conn.close()
	return ''

if __name__ == '__main__':
	try:
		_, verb = sys.argv.pop( 0 ), sys.argv.pop( 0 )
		dispatch = {
			'ul': upload_tar,
			'dl': download_tar,
			'id': lambda *args: ' '.join( [ SIGNATURE.split( ':' )[ 0 ], INFO ] )
		}
		res = dispatch[ verb ]( *sys.argv )
		if res: print res
	except KeyError:
		sys.exit( 'Wrong verb' )
	except IndexError:
		sys.exit( 'Wrong number of args' )
