from gettext import GNUTranslations, NullTranslations
from io import BytesIO
from os.path import dirname
from zipfile import ZipFile

PACKAGE_PATH = dirname( dirname( __file__ ) )

def translation( lang ):
	try:
		with ZipFile( PACKAGE_PATH ) as f:
			mo = f.read( 'tm/mos/{0}.mo'.format( lang ) )
	except KeyError:
		return NullTranslations()
	else:
		return GNUTranslations( BytesIO( mo ) )
