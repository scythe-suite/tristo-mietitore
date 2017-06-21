from argparse import ArgumentParser

from tm.client import tar, untar, lstar

def read_uids(path):
	with open( path, 'r' ) as f:
		try:
			uids = dict( ( line.decode( 'utf8' ).strip().split( '\t' ) for line in f if line != '\n' and not line.startswith( '#' ) ) )
		except ValueError:
			raise ValueError( 'A line of the UIDs file "{}" does not contain exactly one tab'.format( path ) )
	return uids

def main():

	parser = ArgumentParser( prog = 'tm mkconf' )
	parser.add_argument( 'tar_dir', help = 'The directory to include as TAR_DATA' )
	parser.add_argument( '--base_conf', '-b', help = 'The configuration file to start with' )
	parser.add_argument( '--registerd_uids', '-r', help = 'A tab separated file of (uid, data) pairs to include as REGISTERED_UIDS' )
	parser.add_argument( '--upload_dir', '-u', help = 'The (absolute) path of the upload directory' )
	parser.add_argument( '--filter', '-f', default = '.*', help = 'A regular expression files to be included in TAR_DATA must match' )
	parser.add_argument( '--verbose', '-v', action='store_true', help = 'Whether to show the files added to TAR_DATA' )
	parser.add_argument( 'output_conf', help = 'The resulting configuration file' )

	args = parser.parse_args()

	with open( args.output_conf, 'w' ) as out:

		if args.base_conf:
			with open( args.base_conf, 'r' ) as f: base_conf = f.read()
			out.write( base_conf + '\n' )

		if args.upload_dir:
			out.write( '\nUPLOAD_DIR = ' + repr( args.upload_dir ) + '\n' )

		tar_data = tar( args.tar_dir, args.filter, args.verbose )
		out.write( 'TAR_DATA = """\n' + tar_data + '"""\n' )

		if args.registerd_uids:
			out.write( '\nREGISTERED_UIDS = ' + repr( read_uids( args.registerd_uids ) ) + '\n' )

if __name__ == '__main__':
	main()
