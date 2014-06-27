import logging
from config import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


stellar_db = create_engine(config['stellar_url'], echo=False)
db = create_engine(config['url'], echo=False)
raw_connection = db.connect()
raw_connection.connection.set_isolation_level(0)
Base = declarative_base()
db.session = sessionmaker(bind=db)()
stellar_db.session = sessionmaker(bind=stellar_db)()

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)
