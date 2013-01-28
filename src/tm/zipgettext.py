from errno import ENOENT
from gettext import GNUTranslations, NullTranslations
from io import BytesIO

from pkg_resources import resource_string

def translation( lang ):
	try:
		mo = resource_string( 'tm', 'mos/{0}.mo'.format( lang ) )
	except IOError as e:
		if e.errno == ENOENT: return NullTranslations()
		else: raise
	else:
		return GNUTranslations( BytesIO( mo ) )
