from sys import argv

from tm import mkconf, web

if __name__ == '__main__':
	dispatch = {
		'web': web.main,
		'mkconf': mkconf.main
	}
	try:
		dispatch[ argv.pop( 1 ) ]()
	except ( IndexError, KeyError ):
		print 'usage: python {0} {{web,mkconf}} ...'.format( argv[ 0 ] )
	except:
		raise
