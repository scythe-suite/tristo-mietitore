import sys

if __name__ == '__main__':
	if sys.argv[ 1 ] == 'tar':
		l = {}
		_excepthook = sys.excepthook
		execfile( './eegat/templates/client.py', l )
		sys.excepthook = _excepthook
		print l['tar']()
	elif sys.argv[ 1 ] == 'serve':
		from eegat.web import app
		app.run( host= '0.0.0.0', port = 8000, debug = len( sys.argv ) == 2 )
