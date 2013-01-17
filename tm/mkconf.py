import sys; _excepthook = sys.excepthook

import argparse
from os.path import join, dirname

loc = {}
execfile( join( dirname( __file__ ), 'templates', 'client.py' ), loc )
sys.excepthook = _excepthook
tar = loc[ 'tar' ]

def main():

	parser = argparse.ArgumentParser()
	parser.add_argument( 'output_conf_file', help = 'The resulting configuration file' )
	parser.add_argument( 'base_conf_file', help = 'The configuration file to start with' )
	parser.add_argument( 'tar_dir', help = 'The directory to include as TAR_DATA' )
	parser.add_argument( 'registerd_uids_file', help = 'A tab separated file of (uid, data) pairs to include as REGISTERED_UIDS', nargs = '?' )
	args = parser.parse_args()

	with open( args.base_conf_file, 'r' ) as f: base_conf = f.read()

	tar_data = tar( args.tar_dir, verbose = False )

	if args.registerd_uids_file:
		with open( args.registerd_uids_file, 'r' ) as f:
			registered_uids = dict( ( line.strip().split( '\t' ) for line in f if line != '\n' and not line.startswith( '#' ) ) )
	else:
		registered_uids = None

	with open( args.output_conf_file, 'w' ) as f:
		f.write( base_conf + '\n' )
		f.write( 'TAR_DATA = """\n' + tar_data + '"""\n' )
		if registered_uids: f.write( '\nREGISTERED_UIDS = ' + repr( registered_uids ) + '\n' )

if __name__ == '__main__':
	main()
