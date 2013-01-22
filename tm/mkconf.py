import sys; _excepthook = sys.excepthook

from argparse import ArgumentParser
from os.path import join, dirname

loc = {}
execfile( join( dirname( __file__ ), 'templates', 'client.py' ), loc )
sys.excepthook = _excepthook
tar, untar, lstar = loc[ 'tar' ], loc[ 'untar' ], loc[ 'lstar' ]


def main():

	parser = ArgumentParser()
	parser.add_argument( 'output_conf', help = 'The resulting configuration file' )
	parser.add_argument( 'base_conf', help = 'The configuration file to start with' )
	parser.add_argument( 'tar_dir', help = 'The directory to include as TAR_DATA' )
	parser.add_argument( 'registerd_uids', help = 'A tab separated file of (uid, data) pairs to include as REGISTERED_UIDS', nargs = '?' )
	parser.add_argument( '--filter', '-f', default = '.*', help = 'A regular expression files to be included in TAR_DATA must match' )
	parser.add_argument( '--verbose', '-v', default = False, action='store_true', help = 'Whether to show the files added to TAR_DATA' )

	args = parser.parse_args()

	with open( args.base_conf, 'r' ) as f: base_conf = f.read()

	tar_data = tar( args.tar_dir, args.filter, args.verbose )

	if args.registerd_uids:
		with open( args.registerd_uids, 'r' ) as f:
			registered_uids = dict( ( line.decode( 'utf8' ).strip().split( '\t' ) for line in f if line != '\n' and not line.startswith( '#' ) ) )
	else:
		registered_uids = None

	with open( args.output_conf, 'w' ) as f:
		f.write( base_conf + '\n' )
		f.write( 'TAR_DATA = """\n' + tar_data + '"""\n' )
		if registered_uids: f.write( '\nREGISTERED_UIDS = ' + repr( registered_uids ) + '\n' )

if __name__ == '__main__':
	main()
