from importlib import import_module
from sys import argv

if __name__ == '__main__':
	try:
		import_module( 'tm.{0}'.format( argv.pop( 1 ) ) ).main()
	except ( IndexError, ImportError ):
		print 'usage: python {0} {{web,mkconf}} ...'.format( argv[ 0 ] )
	except:
		raise