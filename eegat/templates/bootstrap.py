from base64 import decodestring
from os import environ, chmod, execlp
from os.path import join
from subprocess import check_call
from string import Template

try:
	EEG_HOME = environ[ 'EEG_HOME' ]
	print 'Installing in {0}...'.format( EEG_HOME )
except KeyError:
	EEG_HOME = environ[ 'HOME' ]

client = decodestring( """
{{ client }}""" )

client = Template( client ).substitute( eeg_home = EEG_HOME )
dest = join( EEG_HOME, '.lec' )
with open( dest, 'w' ) as f:
	f.write( client )
chmod( dest, 0700 )

check_call( [ dest, 'dl' ] )

environ[ 'PATH' ] = '{0}/bin:{1}'.format( EEG_HOME, environ[ 'PATH' ] )
execlp( 'bash', 'bash' )
