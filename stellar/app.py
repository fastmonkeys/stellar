import logging
from config import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.declarative import declarative_base


class Stellar(object):
    def __init__(self):
        self.init_database()
        self.create_stellar_database()

    def init_database(self):
        self.db = create_engine(config['stellar_url'], echo=False)
        self.raw_db = create_engine(config['url'], echo=False)
        self.raw_conn = self.db.connect()
        self.raw_conn.connection.set_isolation_level(0)
        self.base = declarative_base()
        self.db.session = sessionmaker(bind=self.db)()
        self.raw_db.session = sessionmaker(bind=self.raw_db)()

        logging.basicConfig()
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)

    def create_stellar_database(self):
        try:
            self.raw_conn.execute('''
                CREATE DATABASE "stellar_data"
            ''')
        except ProgrammingError:
            return False
        self.base.metadata.create_all(self.db)
        self.db.session.commit()

    def get_snapshot(self, snapshot_name):
        return self.stellar_db.session.query(Snapshot).filter(
            Snapshot.name == snapshot_name,
        ).count() > 0

    def get_snapshots(self):
        return self.stellar_db.session.query(
            Snapshot
        ).order_by(
            Snapshot.created_at.desc()
        ).all()

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
