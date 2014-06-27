import argparse
import sys
import hashlib
import uuid
import os

from database import *
from config import config
from models import Snapshot
from operations import create_stellar_tables, copy_database


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
        parser.add_argument('name')
        args = parser.parse_args(sys.argv[2:])

        print "Snapshotting tracked databases: %s" % ', '.join(config['tracked_databases'])
        table_hash = hashlib.md5(str(uuid.uuid4())).hexdigest()
        for table_name in config['tracked_databases']:
            copy_database(table_name, 'stellar_%s_primary' % table_hash)
            snapshot = Snapshot(
                table_name=table_name,
                table_hash=table_hash,
                project_name=config['project_name'],
                name=args.name
            )
            stellar_db.session.add(snapshot)
        stellar_db.session.commit()
        if os.fork():
            return

        for table_name in config['tracked_databases']:
            copy_database(table_name, 'stellar_%s_slave' % table_hash)


if __name__ == '__main__':
    create_stellar_tables()
    CommandApp()
    #
    # stellar
    # 1. Snapshot current database
    # stellar snapshot <name> (--git)
    # stellar rollback <name> (--git)
    # stellar list
    # stellar remove
