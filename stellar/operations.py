from sqlalchemy.exc import ProgrammingError


def terminate_database_connections(raw_conn, database):
    raw_conn.execute(
        '''
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE
                pg_stat_activity.datname = '%s' AND
                pid <> pg_backend_pid();
        ''' % database
    )


def create_database(raw_conn, database):
    terminate_database_connections(raw_conn, database)
    raw_conn.execute(
        '''
            CREATE DATABASE "%s";
        ''' %
        (
            database
        )
    )


def copy_database(raw_conn, from_database, to_database):
    terminate_database_connections(raw_conn, from_database)
    raw_conn.execute(
        '''
            CREATE DATABASE "%s" WITH TEMPLATE "%s";
        ''' %
        (
            to_database,
            from_database
        )
    )


def database_exists(raw_conn, database):
    return raw_conn.execute(
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

def rename_database(raw_conn, from_database, to_database):
    raw_conn.execute(
        '''
            ALTER DATABASE "%s" RENAME TO "%s"
        ''' %
        (
            from_database,
            to_database
        )
    )


def remove_database(raw_conn, database):
    terminate_database_connections(raw_conn, database)
    raw_conn.execute(
        '''
            DROP DATABASE "%s"
        ''' %
        (
            database
        )
    )
