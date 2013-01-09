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
	environ[ 'EEG_HOME' ] = EEG_HOME

client = decodestring( """
{{ client }}""" )

client = Template( client ).substitute( eeg_home = EEG_HOME )
dest = join( EEG_HOME, '.lec' )
with open( dest, 'w' ) as f:
	f.write( client )
chmod( dest, 0700 )
check_call( [ dest, 'dl' ] )

environ[ 'PATH' ] = '{0}/bin:{1}'.format( EEG_HOME, environ[ 'PATH' ] )
profile = join( environ[ 'HOME' ], '.bash_profile' )
path_setup ="""
# setup the EEG_PATH
export PATH={0}/bin:$PATH
# don't delete this line and the above one
""".format( EEG_HOME )
with open( profile, 'r' ) as f:
	tmp = f.read()
if tmp.find( 'EEG_HOME' ) == -1:
	with open( profile, 'a' ) as f:
		f.write( path_setup )

execlp( 'bash', 'bash' )
