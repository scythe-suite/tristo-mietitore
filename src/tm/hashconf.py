from argparse import ArgumentParser
from hmac import new as mac
from hashlib import sha256

from tm.client import untar

def main():

	parser = ArgumentParser( prog = 'tm hashconf' )
	parser.add_argument( 'conf_file', help = 'The configuration file' )

	args = parser.parse_args()

	conf_file = {}
	with open( args.conf_file, 'r' ) as inf:
		exec inf in conf_file
	print mac( conf_file[ 'SECRET_KEY' ], conf_file[ 'TAR_DATA' ], sha256 ).hexdigest()

if __name__ == '__main__':
	main()
