from importlib import import_module
from sys import argv, stderr, exit
from os.path import dirname

from tm import VERSION

COMMANDS = 'web', 'mkconf', 'untarconf', 'hashconf', 'mkresults'

if __name__ == '__main__':
    try:
        subcommand = argv.pop( 1 )
    except IndexError:
        stderr.write( 'tm: subcommsands: {}\n'.format( ', '.join( COMMANDS ) ) )
        exit( 1 )
    if subcommand == 'version':
        stderr.write( 'tm: version: {}\n'.format( VERSION ) )
        exit( 0 )
    if subcommand not in COMMANDS:
        stderr.write( 'tm: unknown subcommand {}; available subcommsands: {}\n'.format( subcommand, ', '.join( COMMANDS ) ) )
        exit(1)
    try:
        import_module( 'tm.{0}'.format( subcommand ) ).main()
    except KeyboardInterrupt:
        stderr.write( 'tm: premature exit!\n' )
        exit( 1 )
