import argparse
import sys
import hashlib
import uuid
import os
import sys
from time import sleep

from sqlalchemy.exc import ProgrammingError

from config import config
from database import stellar_db, db
from datetime import datetime
from models import Snapshot
from operations import (
    create_stellar_tables,
    copy_database,
    remove_database,
    rename_database,
    database_exists
)
import humanize


class CommandApp(object):
    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Lightning fast database snapshotting for development',
        )
        parser.add_argument(
            'command',
            help='Subcommand to run',
            choices=[unicode(x) for x in dir(self) if not x.startswith('_')],
        )
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

        for table_name in config['tracked_databases']:
            table_hash = hashlib.md5(str(uuid.uuid4())).hexdigest()
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
            snapshot = stellar_db.session.query(Snapshot).filter(
                Snapshot.table_name == table_name,
                Snapshot.name == args.name,
            ).one()
            copy_database(table_name, 'stellar_%s_slave' % snapshot.table_hash)
            snapshot.is_slave_ready = True
            stellar_db.session.commit()

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
                Snapshot.created_at.desc()
            ).all()
        )

    def restore(self):
        parser = argparse.ArgumentParser(
            description='Take a snapshot of the database'
        )
        parser.add_argument('name', nargs='?')
        args = parser.parse_args(sys.argv[2:])

        if not args.name:
            name = stellar_db.session.query(Snapshot).filter(
                Snapshot.project_name == config['project_name']
            ).order_by(Snapshot.created_at.desc()).limit(1).one().name
        else:
            name = args.name

        # Check if slaves are ready
        for snapshot in stellar_db.session.query(Snapshot).filter(
            Snapshot.name == name,
            Snapshot.project_name == config['project_name']
        ):
            if not snapshot.is_slave_ready:
                sys.stdout.write('Waiting for background process to finish')
                sys.stdout.flush()
                while not snapshot.is_slave_ready:
                    sys.stdout.write('.')
                    sys.stdout.flush()
                    sleep(1)
                    stellar_db.session.refresh(snapshot)
                print ''

        for snapshot in stellar_db.session.query(Snapshot).filter(
            Snapshot.name == name,
            Snapshot.project_name == config['project_name']
        ):
            print "Restoring %s" % snapshot.table_name
            if not database_exists('stellar_%s_slave' % snapshot.table_hash):
                print "Database stellar_%s_slave does not exist."
                sys.exit(1)
            remove_database(snapshot.table_name)
            rename_database(
                'stellar_%s_slave' % snapshot.table_hash,
                snapshot.table_name
            )
            snapshot.is_slave_ready = False
            stellar_db.session.commit()

        print "Restore complete."

        if os.fork():
            return

        for snapshot in stellar_db.session.query(Snapshot).filter(
            Snapshot.name == name,
            Snapshot.project_name == config['project_name']
        ):
            copy_database(
                'stellar_%s_master' % snapshot.table_hash,
                'stellar_%s_slave' % snapshot.table_hash
            )
            snapshot.is_slave_ready = True
            stellar_db.session.commit()

    def remove(self):
        parser = argparse.ArgumentParser(
            description='Removes spesified snapshot'
        )
        parser.add_argument('name', default='')
        args = parser.parse_args(sys.argv[2:])

        if not args.name:
            snapshots = stellar_db.session.query(Snapshot).filter(
                Snapshot.project_name == config['project_name']
            ).order_by(Snapshot.created_at.desc())
        else:
            snapshots = stellar_db.session.query(Snapshot).filter(
                Snapshot.project_name == config['project_name'],
                Snapshot.name == args.name
            )
        if not snapshots.count():
            print "Couldn't find snapshot %s" % args.name
            return

        print "Deleting snapshot %s" % args.name
        for table_hash in (s.table_hash for s in snapshots):
            try:
                remove_database('stellar_%s_master' % table_hash)
            except ProgrammingError:
                pass
            try:
                remove_database('stellar_%s_slave' % table_hash)
            except ProgrammingError:
                pass
        snapshots.delete()
        stellar_db.session.commit()
        print "Deleted"


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
