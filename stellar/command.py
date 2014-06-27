import argparse
import sys
import hashlib
import uuid
import os

from config import config
from database import *
from datetime import datetime
from models import Snapshot
from operations import (
    create_stellar_tables,
    copy_database,
    remove_database,
    rename_database
)
import humanize


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

    def list_of_tables(self):
        for row in db.execute('''
            SELECT datname FROM pg_database
            WHERE datistemplate = false
        '''):
            print row[0]

    def gc(self):
        databases = set()
        stellar_databases = set()
        for snapshot in stellar_db.session.query(Snapshot):
            stellar_databases.add(snapshot.table_name)

        for row in db.execute('''
            SELECT datname FROM pg_database
            WHERE datistemplate = false
        '''):
            databases.add(row[0])

        for database in (databases-stellar_databases):
            if database.startswith('stellar_') and database != 'stellar_data':
                remove_database(database)
                print "Removing %s" % database
        print "Garbage collection complete"

    def snapshot(self):
        parser = argparse.ArgumentParser(
            description='Take a snapshot of the database'
        )
        parser.add_argument('name', default='')
        args = parser.parse_args(sys.argv[2:])

        print "Snapshotting tracked databases: %s" % ', '.join(
            config['tracked_databases']
        )
        table_hash = hashlib.md5(str(uuid.uuid4())).hexdigest()
        for table_name in config['tracked_databases']:
            copy_database(table_name, 'stellar_%s_master' % table_hash)
            snapshot = Snapshot(
                table_name=table_name,
                table_hash=table_hash,
                project_name=config['project_name'],
                name=args.name,
            )
            stellar_db.session.add(snapshot)
        stellar_db.session.commit()
        if os.fork():
            return

        for table_name in config['tracked_databases']:
            copy_database(table_name, 'stellar_%s_slave' % table_hash)

    def list(self):
        argparse.ArgumentParser(
            description='List snapshots'
        )

        print '\n'.join(
            '%s %s ago' % (
                s.name,
                humanize.naturaltime(datetime.utcnow() - s.created_at)
            )
            for s in stellar_db.session.query(
                Snapshot
            ).order_by(
                Snapshot.created_at
            ).all()
        )

    def restore(self):
        parser = argparse.ArgumentParser(
            description='Take a snapshot of the database'
        )
        parser.add_argument('name', nargs='?')
        args = parser.parse_args(sys.argv[2:])

        if not args.name:
            table_hash = stellar_db.session.query(Snapshot).filter(
                Snapshot.project_name == config['project_name']
            ).order_by(Snapshot.created_at.desc()).limit(1).one().table_hash
        else:
            table_hash = stellar_db.session.query(Snapshot).filter(
                Snapshot.project_name == config['project_name'],
                Snapshot.name == args.name
            ).one().table_hash

        for snapshot in stellar_db.session.query(Snapshot).filter(
                Snapshot.table_hash == table_hash
        ):
            print "Restoring %s" % snapshot.table_name
            remove_database(snapshot.table_name)
            rename_database(
                'stellar_%s_slave' % table_hash,
                snapshot.table_name
            )

        print "Restore complete."

        if os.fork():
            return

        for snapshot in stellar_db.session.query(Snapshot).filter(
                Snapshot.table_hash == table_hash
        ):
            copy_database(
                'stellar_%s_master' % table_hash,
                'stellar_%s_slave' % table_hash
            )


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
