#
# To use this bootstrap script define the following bash function
#
#	sign() { eval $( python -c "from urllib2 import urlopen; exec urlopen( '{{ request.url_root }}$1' ).read()" ); }
#
# and then invoke it as:
#
#	sign UID
#

# {% if not config.DEBUG %}
import sys; sys.excepthook = lambda t, v, tb: sys.exit( 'An unexpected error occurred!' )
# {% endif %}

from base64 import decodestring
from os import chmod
from os.path import join, expandvars, expanduser
from subprocess import check_output

client = decodestring( """
{{ client }}""" )

evnsetup = """{{ config.ENVIRONMENT_SETUP }}"""

if not client:

	print 'echo "UID not registered"'

else:

	EEG_HOME = expandvars( expanduser( '{{ config.EEG_HOME }}' ) )

	print 'echo -n "Installing in {0}... ";'.format( EEG_HOME )

	dest = join( EEG_HOME, '.eeg' )
	with open( dest, 'w' ) as f: f.write( client )
	chmod( dest, 0700 )
	check_output( [ dest, 'se' ] )
	check_output( [ dest, 'dl' ] )

	print '; '.join( ( 'echo done.' + evnsetup.format( EEG_HOME ) ).splitlines() )
