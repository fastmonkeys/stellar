import logging
import hashlib
import uuid
import os
from functools import partial

from stellar.config import load_config
from stellar.models import *
from stellar.operations import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.declarative import declarative_base
from stellar.exceptions import InvalidConfig
from schema import SchemaError


logging.basicConfig()


class Operations(object):
    def __init__(self, raw_connection, config):
        self.terminate_database_connections = partial(
            terminate_database_connections, raw_connection
        )
        self.create_database = partial(create_database, raw_connection)
        self.copy_database = partial(copy_database, raw_connection)
        self.database_exists = partial(database_exists, raw_connection)
        self.rename_database = partial(rename_database, raw_connection)
        self.remove_database = partial(remove_database, raw_connection)


class Stellar(object):
    def __init__(self):
        self.load_config()
        self.init_database()
        self.operations = Operations(self.raw_conn, self.config)

    def load_config(self):
        self.config = load_config()

    def init_database(self):
        self.raw_db = create_engine(self.config['url'], echo=False)
        self.raw_conn = self.raw_db.connect()
        try:
            self.raw_conn.connection.set_isolation_level(0)
        except AttributeError:
            logging.info('Could not set isolation level to 0')

        self.db = create_engine(self.config['stellar_url'], echo=False)
        self.db.session = sessionmaker(bind=self.db)()
        self.raw_db.session = sessionmaker(bind=self.raw_db)()
        tables_missing = self.create_stellar_database()

        if tables_missing:
            self.create_stellar_tables()

        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)

    def create_stellar_database(self):
        try:
            self.raw_conn.execute('CREATE DATABASE "stellar_data"')
            return True
        except ProgrammingError:
            return False

    def create_stellar_tables(self):
        Base.metadata.create_all(self.db)
        self.db.session.commit()

    def get_snapshot(self, snapshot_name):
        return self.db.session.query(Snapshot).filter(
            Snapshot.snapshot_name == snapshot_name,
        ).first()

    def get_snapshots(self):
        return self.db.session.query(
            Snapshot
        ).order_by(
            Snapshot.created_at.desc()
        ).all()

    def get_latest_snapshot(self):
        return self.db.session.query(Snapshot).filter(
            Snapshot.project_name == config['project_name']
        ).order_by(Snapshot.created_at.desc()).first()

    def create_snapshot(self, snapshot_name):
        for table_name in config['tracked_databases']:
            table_hash = hashlib.md5(str(uuid.uuid4())).hexdigest()
            self.operations.copy_database(
                table_name,
                'stellar_%s_master' % table_hash
            )
            snapshot = Snapshot(
                table_name=table_name,
                table_hash=table_hash,
                project_name=config['project_name'],
                name=snapshot_name,
            )
            db.session.add(snapshot)
        db.session.commit()
        if os.fork():
            return

        for table_name in config['tracked_databases']:
            snapshot = db.session.query(Snapshot).filter(
                Snapshot.table_name == table_name,
                Snapshot.snapshot_name == snapshot_name,
            ).one()
            self.operations.copy_database(
                table_name,
                'stellar_%s_slave' % snapshot.table_hash
            )
            snapshot.is_slave_ready = True
            db.session.commit()

    def remove_snapshot(self, snapshot):
        for table_hash in (s.table_hash for s in snapshots):
            try:
                self.operations.remove_database(
                    'stellar_%s_master' % table_hash
                )
            except ProgrammingError:
                pass
            try:
                self.operations.remove_database(
                    'stellar_%s_slave' % table_hash
                )
            except ProgrammingError:
                pass
        snapshots.delete()
        db.session.commit()

    def restore(self, snapshot):
        for snapshot in db.session.query(Snapshot).filter(
            Snapshot.snapshot_name == name,
            Snapshot.project_name == config['project_name']
        ):
            print "Restoring database %s" % snapshot.table_name
            if not database_exists('stellar_%s_slave' % snapshot.table_hash):
                print (
                    "Database stellar_%s_slave does not exist."
                    % snapshot.table_hash
                )
                sys.exit(1)
            self.operations.remove_database(snapshot.table_name)
            self.operations.rename_database(
                'stellar_%s_slave' % snapshot.table_hash,
                snapshot.table_name
            )
            snapshot.is_slave_ready = False
            db.session.commit()

        if os.fork():
            return

        for snapshot in db.session.query(Snapshot).filter(
            Snapshot.snapshot_name == name,
            Snapshot.project_name == config['project_name']
        ):
            self.operations.copy_database(
                'stellar_%s_master' % snapshot.table_hash,
                'stellar_%s_slave' % snapshot.table_hash
            )
            snapshot.is_slave_ready = True
            db.session.commit()

        sys.exit()

    def get_orphan_snapshots(self):
        from models import Snapshot

        databases = set()
        stellar_databases = set()
        for snapshot in db.session.query(Snapshot):
            stellar_databases.add(snapshot.table_name)

        for row in self.raw_db.execute('''
            SELECT datname FROM pg_database
            WHERE datistemplate = false
        '''):
            databases.add(row[0])

        return filter(
            lambda table: (
                table.startswith('stellar_') and
                table != 'stellar_data'
            ),
            (databases-stellar_databases)
        )
