from sqlalchemy.exc import ProgrammingError
from database import stellar_db, db, Base, raw_connection
from models import Snapshot

def create_stellar_tables():
    try:
        raw_connection.execute('''
            CREATE DATABASE "stellar_data"
        ''')
    except ProgrammingError:
        return False
    create_stellar_tables()
    return True


def copy_database(from_database, to_database):
    raw_connection.execute(
        '''
            CREATE DATABASE "%s" WITH TEMPLATE "%s";
        ''' % (
            to_database,
            from_database
        )
    )


def rename_database(from_database, to_database):
    raw_connection.execute(
        '''
            ALTER DATABASE "%s" RENAME TO "%s"
        ''' % (
            from_database,
            to_database
        )
    )


def rename_database(database):
    raw_connection.execute(
        '''
            DROP DATABASE "%s"
        ''' % (
            database
        )
    )