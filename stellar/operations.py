from sqlalchemy.exc import ProgrammingError
from database import stellar_db, db, Base
from models import Snapshot

def create_stellar_tables():
    connection = db.connect()
    connection.connection.set_isolation_level(0)
    try:
        connection.execute('''
            CREATE DATABASE "stellar_data"
        ''')
    except ProgrammingError:
        return False
    connection.close()
    create_stellar_tables()
    return True