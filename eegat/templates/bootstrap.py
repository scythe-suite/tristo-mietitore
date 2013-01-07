from base64 import decodestring
from os import environ, chmod
from os.path import join
from subprocess import check_call

client = decodestring( """
{{ client }}""" )

dest = join( environ[ 'HOME' ], '.lec' )
with open( dest, 'w' ) as f:
	f.write( client )
chmod( dest, 0700 )

check_call( [ dest, 'dl' ] )

#os.environ[ 'PATH' ] = '{}/.bin:{}'.format( os.environ[ 'HOME' ], os.environ[ 'PATH' ] )
#os.execlp( 'bash', 'bash' )
