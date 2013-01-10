import sys
def _excepthook( t, v, tb ):
		tb = extract_tb( tb )[ -1 ]
		f = tb[ 0 ].split( '/' )[ -1 ]
		l = tb[ 1 ]
		e = format_exception_only( t, v )[ -1 ].strip()
		sys.exit( '[{0}:{1}] {2}'.format( f, l, e ) )
sys.excepthook = _excepthook

from base64 import decodestring
from os import chmod
from os.path import join, expandvars, expanduser
from subprocess import check_output
from traceback import extract_tb, format_exception_only

client = decodestring( """
{{ client }}""" )

if not client:

	print 'echo "UID not registered"'

else:

	EEG_HOME = expandvars( expanduser( '{{ config.EEG_HOME }}' ) )

	print 'echo -n "Installing in {0}... ";'.format( EEG_HOME )

	dest = join( EEG_HOME, '.eeg' )
	with open( dest, 'w' ) as f: f.write( client )
	chmod( dest, 0700 )
	check_output( [ dest, 'sp' ] )
	check_output( [ dest, 'dl' ] )

	print 'echo done.; export PATH="{0}/bin":$PATH'.format( EEG_HOME )
