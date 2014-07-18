import logging
import hashlib
import uuid
import os

from config import load_config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.declarative import declarative_base


logging.basicConfig()


class Stellar(object):
    def __init__(self):
        self.load_config()
        self.init_database()
        self.create_stellar_database()

    def load_config(self):
        self.config = load_config()

    def init_database(self):
        self.db = create_engine(self.config['stellar_url'], echo=False)
        self.raw_db = create_engine(self.config['url'], echo=False)
        self.raw_conn = self.db.connect()
        try:
            self.raw_conn.connection.set_isolation_level(0)
        except AttributeError:
            logging.info('Could not set isolation level to 0')

        self.db.session = sessionmaker(bind=self.db)()
        self.raw_db.session = sessionmaker(bind=self.raw_db)()

        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)

    def create_stellar_database(self):
        try:
            self.raw_conn.execute('CREATE DATABASE "stellar_data"')
        except ProgrammingError:
            return False
        self.base.metadata.create_all(self.db)
        self.db.session.commit()

    def get_snapshot(self, snapshot_name):
        return self.stellar_db.session.query(Snapshot).filter(
            Snapshot.name == snapshot_name,
        ).first()

    def get_snapshots(self):
        return self.stellar_db.session.query(
            Snapshot
        ).order_by(
            Snapshot.created_at.desc()
        ).all()

    def get_latest_snapshot(self):
        return self.stellar_db.session.query(Snapshot).filter(
            Snapshot.project_name == config['project_name']
        ).order_by(Snapshot.created_at.desc()).first()


    def create_snapshot(self, snapshot_name):
        for table_name in config['tracked_databases']:
            table_hash = hashlib.md5(str(uuid.uuid4())).hexdigest()
            copy_database(table_name, 'stellar_%s_master' % table_hash)
            snapshot = Snapshot(
                table_name=table_name,
                table_hash=table_hash,
                project_name=config['project_name'],
                name=snapshot_name,
            )
            stellar_db.session.add(snapshot)
        stellar_db.session.commit()
        if os.fork():
            return

        for table_name in config['tracked_databases']:
            snapshot = stellar_db.session.query(Snapshot).filter(
                Snapshot.table_name == table_name,
                Snapshot.name == snapshot_name,
            ).one()
            copy_database(table_name, 'stellar_%s_slave' % snapshot.table_hash)
            snapshot.is_slave_ready = True
            stellar_db.session.commit()

    def remove_snapshot(self, snapshot):
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

    def restore(self, snapshot):
        for snapshot in stellar_db.session.query(Snapshot).filter(
            Snapshot.name == name,
            Snapshot.project_name == config['project_name']
        ):
            print "Restoring database %s" % snapshot.table_name
            if not database_exists('stellar_%s_slave' % snapshot.table_hash):
                print (
                    "Database stellar_%s_slave does not exist."
                    % snapshot.table_hash
                )
                sys.exit(1)
            remove_database(snapshot.table_name)
            rename_database(
                'stellar_%s_slave' % snapshot.table_hash,
                snapshot.table_name
            )
            snapshot.is_slave_ready = False
            stellar_db.session.commit()

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

        sys.exit()

    def get_orphan_snapshots(self):
        from database import stellar_db, db
        from models import Snapshot
        from operations import remove_database

        databases = set()
        stellar_databases = set()
        for snapshot in stellar_db.session.query(Snapshot):
            stellar_databases.add(snapshot.table_name)

        for row in db.execute('''
            SELECT datname FROM pg_database
            WHERE datistemplate = false
        '''):
            databases.add(row[0])

        return filter(
            lambda database: database.startswith('stellar_') and database != 'stellar_data',
            (databases-stellar_databases)
        )
