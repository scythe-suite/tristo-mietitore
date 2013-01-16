# -*- coding: utf-8 -*-
#
# To use this bootstrap script define the following bash function
#
#	sign() { eval $( python -c "from urllib2 import urlopen; exec urlopen( '{{ request.url_root }}$1' ).read()" ); }
#
# and then invoke it as:
#
#	sign UID

echo = lambda message: 'echo "{0}"'.format( message )

{% if client %}

{% if not config.DEBUG %}
import sys; sys.excepthook = lambda t, v, tb: sys.exit( """{{ _( "An unexpected installation error occurred!" ) }}""" )
{%- endif %}

from base64 import decodestring
from errno import EEXIST
from os import chmod, makedirs
from os.path import join, expandvars, expanduser, isdir
from subprocess import check_output

EEG_HOME = expandvars( expanduser( '{{ config.EEG_HOME }}' ) )
ENVIRONMENT_SETUP = """{{ config.ENVIRONMENT_SETUP }}"""
DATA = '{{ data }}'
CLIENT = decodestring( """
{{ client }}""" )

try:
	makedirs( EEG_HOME )
except OSError as e:
	if e.errno == EEXIST and isdir( EEG_HOME ): pass
	else: raise RuntimeError( '{0} exists and is not a directory'.format( EEG_HOME ) )

dest = join( EEG_HOME, '.eeg' )
with open( dest, 'w' ) as f: f.write( CLIENT )
chmod( dest, 0700 )
check_output( [ dest, 'se' ] )
check_output( [ dest, 'dl' ] )

print '; '.join( [ echo( """{{ _( "Installed in {eeg_home} for: {data}" ) }}""".format( eeg_home = EEG_HOME, data = DATA ) ) ] + [ _ for _ in ENVIRONMENT_SETUP.format( EEG_HOME ).splitlines() if _ ] )

{% elif data %}

print echo( """{{ _( "UID already signed as: {data}" ) }}""".format( data = '{{ data }}' ) )

{% else %}

print echo( """{{ _( "UID not registered" ) }}""" )

{%- endif -%}
