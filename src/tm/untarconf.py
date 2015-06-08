from argparse import ArgumentParser

from pkg_resources import resource_string

loc = {}
exec resource_string( 'tm', 'templates/client.pyt' ) in loc
untar = loc[ 'untar' ]

def main():

	parser = ArgumentParser( prog = 'tm untarconf' )
	parser.add_argument( 'conf_file', help = 'The configuration file' )
	parser.add_argument( 'output_dir', help = 'The directory where to extract TAR_DATA' )

	args = parser.parse_args()

	conf_file = {}
	with open( args.conf_file, 'r' ) as inf:
		exec inf in conf_file
	tar_data = conf_file[ 'TAR_DATA' ]
	untar( tar_data, args.output_dir )

if __name__ == '__main__':
	main()
