#
# To use this bootstrap script define the following bash function
#
#	sign() { eval $( python -c "from urllib2 import urlopen; exec urlopen( '{{ request.url_root }}$1' ).read()" ); }
#
# and then invoke it as:
#
#	sign UID
# {% if client %}

# {% if not config.DEBUG %}
import sys; sys.excepthook = lambda t, v, tb: sys.exit( 'An unexpected error occurred!' )
# {% endif %}

from base64 import decodestring
from os import chmod
from os.path import join, expandvars, expanduser
from subprocess import check_output

DATA = '{{ data }}'
ENVIRONMENT_SETUP = """{{ config.ENVIRONMENT_SETUP }}"""
CLIENT = decodestring( """
{{ client }}""" )

EEG_HOME = expandvars( expanduser( '{{ config.EEG_HOME }}' ) )

print 'echo -n "Installing in {0} for \'{1}\'... ";'.format( EEG_HOME, DATA )

dest = join( EEG_HOME, '.eeg' )
with open( dest, 'w' ) as f: f.write( CLIENT )
chmod( dest, 0700 )
check_output( [ dest, 'se' ] )
check_output( [ dest, 'dl' ] )

print '; '.join( ( 'echo done.' + ENVIRONMENT_SETUP.format( EEG_HOME ) ).splitlines() )

# {% elif data %}

print 'echo "UID already signed as \'{{ data }}\'"'

# {% else %}

print 'echo "UID not registered"'

# {% endif %}
