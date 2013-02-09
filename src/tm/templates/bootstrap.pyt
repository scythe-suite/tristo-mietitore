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

{% if client_code %}

{% if not config.DEBUG %}
import sys; sys.excepthook = lambda t, v, tb: sys.exit( """{{ _( "An unexpected installation error occurred!" ) }}""" )
{%- endif %}

from base64 import decodestring
from errno import EEXIST, ENOENT
from os import chmod, makedirs
from os.path import join, expandvars, expanduser, isdir, abspath
from subprocess import check_output

HOME = abspath( expandvars( expanduser( """{{ config.HOME }}""" ) ) )
CLIENT_PATH = abspath( expandvars( expanduser( """{{ config.CLIENT_PATH }}""".replace( '### home ###', HOME ) ) ) )
ENVIRONMENT_SETUP = """{{ config.ENVIRONMENT_SETUP }}""".replace( '### home ###', HOME )
CLIENT_CODE = decodestring( """{{ client_code }}""" ).replace( '### home ###', HOME )
INFO = """{{ info }}"""

try:
	makedirs( HOME, 0700 )
except OSError as e:
	if e.errno == EEXIST and isdir( HOME ): pass
	else: raise RuntimeError( '{0} exists and is not a directory'.format( HOME ) )

with open( CLIENT_PATH, 'w' ) as f: f.write( CLIENT_CODE )
chmod( CLIENT_PATH, 0700 )

if ENVIRONMENT_SETUP:
	profile = expanduser( '~/.bash_profile' )
	comment = '# EEG environment setup'
	to_append = comment + ENVIRONMENT_SETUP
	try:
		tmp = ''
		with open( profile, 'r' ) as f: tmp = f.read()
	except IOError as e:
		if e.errno == ENOENT: pass
		else: raise RuntimeError( 'Failed to read ~/.bash_profile' )
	if tmp.find( comment ) != -1:
		echo( """{{ _( "Warning: ~/.bash_profile already contains EEG environment setup" ) }}""" )
	else:
		with open( profile, 'a' ) as f: f.write( '\n' + to_append + '\n' )

check_output( [ CLIENT_PATH, 'dl' ] )

echoes = [ echo( """{{ _( "Installed in {home} for: {info}" ) }}""".format( home = HOME, info = INFO.replace( '"', r'\"' ) ) ) ]
if ENVIRONMENT_SETUP: echoes.extend(  _ for _ in ENVIRONMENT_SETUP.splitlines() if _ )
print '; '.join(  echoes  )

{% elif info %}

print echo( """{{ _( "UID already signed as: {info}" ) }}""".format( info = """{{ info }}""" ) )

{% else %}

print echo( """{{ _( "UID not registered" ) }}""" )

{%- endif -%}
