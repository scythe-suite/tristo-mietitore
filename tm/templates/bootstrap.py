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

TM_HOME = expandvars( expanduser( '{{ config.TM_HOME }}' ) )
ENVIRONMENT_SETUP = """{{ config.ENVIRONMENT_SETUP }}"""
DATA = '{{ data }}'
CLIENT = decodestring( """
{{ client }}""" )

try:
	makedirs( TM_HOME )
except OSError as e:
	if e.errno == EEXIST and isdir( TM_HOME ): pass
	else: raise RuntimeError( '{0} exists and is not a directory'.format( TM_HOME ) )

dest = join( TM_HOME, '.tm' )
with open( dest, 'w' ) as f: f.write( CLIENT )
chmod( dest, 0700 )
check_output( [ dest, 'se' ] )
check_output( [ dest, 'dl' ] )

print '; '.join( [ echo( """{{ _( "Installed in {tm_home} for: {data}" ) }}""".format( tm_home = TM_HOME, data = DATA ) ) ] + [ _ for _ in ENVIRONMENT_SETUP.format( TM_HOME ).splitlines() if _ ] )

{% elif data %}

print echo( """{{ _( "UID already signed as: {data}" ) }}""".format( data = '{{ data }}' ) )

{% else %}

print echo( """{{ _( "UID not registered" ) }}""" )

{%- endif -%}
