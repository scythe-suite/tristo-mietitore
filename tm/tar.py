import sys; _excepthook = sys.excepthook

from os.path import join, dirname

loc = {}
execfile( join( dirname( __file__ ), 'templates', 'client.py' ), loc )
sys.excepthook = _excepthook
tar = loc[ 'tar' ]

if __name__ == '__main__':
	print tar( *sys.argv[ 1: ] )
