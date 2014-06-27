import argparse
import sys

from database import *


class CommandApp(object):
    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Lightning fast database snapshotting for development',
        )
        parser.add_argument('command', help='Subcommand to run')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print 'Unrecognized command'
            parser.print_help()
            exit(1)
        getattr(self, args.command)()

    def snapshot(self):
        parser = argparse.ArgumentParser(
            description='Take a snapshot of the database'
        )
        parser.add_argument('--amend', action='store_true')
        args = parser.parse_args(sys.argv[2:])
        print "Snapshot"


if __name__ == '__main__':
    CommandApp()
    #
    # stellar
    # 1. Snapshot current database
    # stellar snapshot --branch
    # stellar rollback --branch
    # stellar list
    # stellar remove