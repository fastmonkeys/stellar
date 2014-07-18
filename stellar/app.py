import logging
import hashlib
import uuid
import os
import sys
from functools import partial

from config import load_config, InvalidConfig
from models import Snapshot, Table, Base
from operations import (
    copy_database,
    create_database,
    database_exists,
    remove_database,
    rename_database,
    terminate_database_connections,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.declarative import declarative_base
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
            Snapshot.project_name == self.config['project_name']
        ).first()

    def get_snapshots(self):
        return self.db.session.query(
            Snapshot.project_name == self.config['project_name']
        ).order_by(
            Snapshot.created_at.desc()
        ).all()

    def get_latest_snapshot(self):
        return self.db.session.query(Snapshot).filter(
            Snapshot.project_name == self.config['project_name']
        ).order_by(Snapshot.created_at.desc()).first()

    def create_snapshot(self, snapshot_name, before_copy=None):
        snapshot = Snapshot(
            snapshot_name=snapshot_name,
            project_name=self.config['project_name']
        )
        self.db.session.add(snapshot)

        for table_name in self.config['tracked_databases']:
            if before_copy:
                before_copy(table_name)
            table = Table(
                table_name=table_name,
                snapshot=snapshot,
                slave_pid=1
            )
            self.operations.copy_database(
                table_name,
                table.get_table_name('master')
            )
            self.db.session.add(table)
        self.db.session.commit()

        if os.fork():
            return

        for table in snapshot.tables:
            table.slave_pid = os.getpid()
            self.db.session.commit()
            self.operations.copy_database(
                table.get_table_name('master'),
                table.get_table_name('slave')
            )
            table.slave_pid = None
            self.db.session.commit()


    def remove_snapshot(self, snapshot):
        try:
            self.operations.remove_database(
                snapshot.get_table_name('master')
            )
        except ProgrammingError:
            pass
        try:
            self.operations.remove_database(
                snapshot.get_table_name('slave')
            )
        except ProgrammingError:
            pass
        snapshot.delete()
        self.db.session.commit()

    def restore(self, snapshot):
        for table in snapshot.tables:
            print "Restoring database %s" % table.table_name
            if not database_exists(table.get_table_name('slave')):
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
        snapshot.slave_pid = 1
        self.db.session.commit()

        pid = os.fork()
        if pid:
            snapshot.slave_pid = pid
            self.db.session.commit()
            return

        for table in snapshot.tables:
            self.operations.copy_database(
                table.get_table_name('master'),
                table.get_table_name('slave')
            )
        snapshot.slave_pid = None
        self.db.session.commit()

        sys.exit()

    def get_orphan_snapshots(self):
        from models import Snapshot

        databases = set()
        stellar_databases = set()
        for snapshot in self.db.session.query(Snapshot):
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

    @property
    def default_snapshot_name(self):
        n = 1
        while self.db.session.query(Snapshot).filter(
            Snapshot.snapshot_name == 'snap%d' % n,
            Snapshot.project_name == self.config['project_name']
        ).count():
            n += 1
        return 'snap%d' % n
