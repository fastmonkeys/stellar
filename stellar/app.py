import logging
from config import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


class Stellar(object):
    def __init__(self):
        self.init_database()
        self.create_stellar_database()

    def init_database(self):
        self.db = create_engine(config['stellar_url'], echo=False)
        self.raw_db = create_engine(config['url'], echo=False)
        self.raw_conn = db.connect()
        self.raw_conn.connection.set_isolation_level(0)
        Base = declarative_base()
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
        Base.metadata.create_all(self.db)
        self.db.session.commit()