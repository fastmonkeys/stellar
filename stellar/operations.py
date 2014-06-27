from sqlalchemy.exc import ProgrammingError
from database import stellar_db, Base, raw_connection


def create_stellar_tables():
    try:
        raw_connection.execute('''
            CREATE DATABASE "stellar_data"
        ''')
    except ProgrammingError:
        return False
    Base.metadata.create_all(stellar_db)
    stellar_db.session.commit()
    return True


def terminate_database_connections(database):
    raw_connection.execute(
        '''
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE
                pg_stat_activity.datname = '%s' AND
                pid <> pg_backend_pid();
        ''' % database
    )


def copy_database(from_database, to_database):
    terminate_database_connections(from_database)
    raw_connection.execute(
        '''
            CREATE DATABASE "%s" WITH TEMPLATE "%s";
        ''' %
        (
            to_database,
            from_database
        )
    )


def database_exists(database):
    return raw_connection.execute(
        '''
            SELECT COUNT(*)
            FROM pg_database
            WHERE
            datistemplate is false AND
            datname = '%s';
        ''' %
        (
            database
        )
    ).first()[0] > 0

def rename_database(from_database, to_database):
    raw_connection.execute(
        '''
            ALTER DATABASE "%s" RENAME TO "%s"
        ''' %
        (
            from_database,
            to_database
        )
    )


def remove_database(database):
    raw_connection.execute(
        '''
            DROP DATABASE "%s"
        ''' %
        (
            database
        )
    )
