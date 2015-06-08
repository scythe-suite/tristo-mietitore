from argparse import ArgumentParser, REMAINDER, FileType
from collections import namedtuple
from json import dumps
from logging import basicConfig, getLogger, DEBUG, INFO
from operator import itemgetter
from os import walk
from os.path import join, normpath
from re import compile as recompile

LOG_LEVEL = INFO
basicConfig( format = '%(asctime)s %(levelname)s: %(funcName)s %(message)s', datefmt = '%Y-%m-%d %H:%M:%S', level = LOG_LEVEL )
LOGGER = getLogger( __name__ )

PATTERN_KINDS = SIGNATURE, SOURCE, SOURCES, CASE, CASES = 'signature', 'source', 'sources', 'case', 'cases'

class ScannerTracker( type ):
	SCANNERS = []
	def __new__( cls, name, bases, dct ):
		new = super( ScannerTracker, cls).__new__( cls, name, bases, dct )
		cls.SCANNERS.append( ( dct[ 'SHORT_NAME' ], new ) )
		return new

class FileSystemScanner( object ):

	__metaclass__ = ScannerTracker

	SHORT_NAME = 'fs'
	SIGNATURE_PATTERN = None
	SOURCE_PATTERN = None
	SOURCES_PATTERN = None
	CASE_PATTERN = None
	CASES_PATTERN = None

	def default_reader( self, path ):
		with open( path, 'rb' ) as f: content = unicode( f.read(), errors = 'replace' )
		return content

	def __init__( self, basedir, *args, **kwargs ):
		self.basedir = normpath( basedir )
		self.patterns = {}
		self.readers = {}
		for kind in PATTERN_KINDS:
			pattern = getattr( self, kind.upper() + '_PATTERN' )
			if pattern:
				self.patterns[ kind ] = recompile( join( self.basedir, pattern ) )
				try:
					self.readers[ kind ] = getattr( self, kind + '_reader' )
				except AttributeError:
					self.readers[ kind ] = self.default_reader
		if LOGGER.isEnabledFor( DEBUG ):
			LOGGER.debug( 'Using the following patterns and readers...' )
			for kind, pattern in self.patterns.items():
				LOGGER.debug( 'Kind {0}, pattern = {1}, reader = {2}'.format( kind, pattern.pattern, self.readers[ kind ] ) )

	def scan( self ):

		def _to_keys( match ):
			_Keys = namedtuple( 'Keys', 'uid,exercise,source,case' )
			keys = _Keys( None, None, None, None )._replace( **match.groupdict() )
			if not keys.uid: raise RuntimeError( 'Match must contains at least "uid"' )
			return keys

		results = {}

		def _assign( kind, keys, content ):
			if keys.uid not in results:
				results[ keys.uid ] = {
					'signature': { 'uid': keys.uid, 'info': keys.uid, 'ip': '' },
					'exercises': {}
				}
			if keys.exercise and keys.exercise not in results[ keys.uid ][ 'exercises' ]:
				results[ keys.uid ][ 'exercises' ][ keys.exercise ] = {
					'sources': {},
					'cases': {}
				}
			if kind == SIGNATURE:
				results[ keys.uid ][ 'signature' ] = content
			elif kind == SOURCE:
				results[ keys.uid ][ 'exercises' ][ keys.exercise ][ 'sources' ][ keys.source ] = content
			elif kind == SOURCES:
				results[ keys.uid ][ 'exercises' ][ keys.exercise ][ 'sources' ] = content
			elif kind == CASE:
				results[ keys.uid ][ 'exercises' ][ keys.exercise ][ 'cases' ][ keys.case ] = content
			elif kind == CASES:
				results[ keys.uid ][ 'exercises' ][ keys.exercise ][ 'cases' ] = content
			else: raise RuntimeError( 'Unkown kind: "{0}"'.format( kind ) )

		# scan (using dicts)

		exercise_names = set()
		for root, dirs, files in walk( self.basedir, followlinks = True ):
			for name in files:
				path = join( root, name )
				for kind, pattern in self.patterns.items():
					match = pattern.match( path )
					if match:
						keys = _to_keys( match )
						if keys.exercise: exercise_names.add( keys.exercise )
						LOGGER.info( 'Match of kind {0}, {1}'.format( kind, keys ) )
						value = self.readers[ kind ]( path )
						_assign( kind, keys, value )

		# fix (transforming dicts in lists)

		self.results = []
		for uid, res in results.items():
			exercises = []
			for exercise_name in exercise_names:
				try:
					exercise = res[ 'exercises' ][ exercise_name ]
				except KeyError:
					exercise = { 'name': exercise_name, 'sources': [], 'cases': [] }
				exercise[ 'name' ] = exercise_name
				if isinstance( exercise[ 'sources' ], dict ):
					sources = []
					for source_name, source in exercise[ 'sources' ].items():
						sources.append( { 'name': source_name, 'content': source } )
					exercise[ 'sources' ] = sources
				if isinstance( exercise[ 'sources' ], dict ):
					cases = []
					for case_name, case in exercise[ 'cases' ].items():
						case[ 'name' ] = case_name
						cases.append( case )
					exercise[ 'cases' ] = cases
				exercises.append( exercise )
			res[ 'exercises' ] = exercises
			self.results.append( res )

		return self

	def sort( self ):
		self.results.sort( key = lambda _: _[ 'signature' ][ 'uid' ] )
		return self

	def tojson( self ):
		return dumps( self.results )


class OneExercisePerFileScanner( FileSystemScanner ):

	SHORT_NAME = '1f'
	SOURCE_PATTERN = r'(?P<uid>.*)/(?P<source>(?P<exercise>.*)\.{0})$'

	def __init__( self, basedir, extension = None ):
		if not extension: extension = '.+'
		self.SOURCE_PATTERN = self.SOURCE_PATTERN.format( extension )
		super( OneExercisePerFileScanner, self ).__init__( basedir )


class OneExercisePerDirectoryScanner( FileSystemScanner ):

	SHORT_NAME = '1d'
	SOURCE_PATTERN = r'(?P<uid>.*)/(?P<exercise>.*)/(?P<source>.*\.{0})$'

	def __init__( self, basedir, extension = None ):
		if not extension: extension = '.+'
		self.SOURCE_PATTERN = self.SOURCE_PATTERN.format( extension )
		super( OneExercisePerDirectoryScanner, self ).__init__( basedir )


class TristoMietitoreScanner( OneExercisePerDirectoryScanner ):

	SHORT_NAME = 'tm'
	SIGNATURE_PATTERN = r'(?P<uid>.*)/SIGNATURE\.tsv'

	def signature_reader( self, path ):
		with open( path, 'rb' ) as f: content = unicode( f.read(), errors = 'replace' )
		s = {}
		s[ 'uid' ], s[ 'info' ], s[ 'ip' ] = content.strip().split( '\t' )
		return s


SCANNERS = ScannerTracker.SCANNERS

def main():

	parser = ArgumentParser( prog = 'tm mkresults' )
	parser.add_argument( '--scanner', '-s', help = 'The scanner to use (default: {0}; available: {1})'.format( SCANNERS[ -1 ][ 0 ], ', '.join( map( itemgetter( 0 ), SCANNERS ) ) ) )
	parser.add_argument( 'results_dir', help = 'The directory where the results where stored' )
	parser.add_argument( 'json_output', help = 'The file where to store the json summary', type = FileType( 'wb' ) )
	parser.add_argument( 'extra_args', help = 'Extra arguments, passed to the scanner', nargs = REMAINDER )
	args = parser.parse_args()

	scanner = None
	try:
		scanner = dict( SCANNERS )[ args.scanner ] if args.scanner else SCANNERS[ -1 ][ 1 ]
	except KeyError:
		parser.error( 'Scanner "{0}" not found; use -h to obtains a list of available scanners.'.format( args.scanner ) )

	args.json_output.write( scanner( args.results_dir, *args.extra_args ).scan().sort().tojson() )
	args.json_output.close()
