import sqlalchemy_utils


SUPPORTED_DIALECTS = (
    'postgresql',
    'mysql'
)

class NotSupportedDatabase(Exception):
    pass


def terminate_database_connections(raw_conn, database):
    if raw_conn.engine.dialect.name == 'postgresql':
        raw_conn.execute(
            '''
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE
                    pg_stat_activity.datname = '%s' AND
                    pid <> pg_backend_pid();
            ''' % database
        )
    else:
        # NotYetImplemented
        pass


def create_database(raw_conn, database):
    return sqlalchemy_utils.functions.create_database(
        '%s%s' % (raw_conn.engine.url, database)
    )


def copy_database(raw_conn, from_database, to_database):
    terminate_database_connections(raw_conn, from_database)

    if raw_conn.engine.dialect.name == 'postgresql':
        raw_conn.execute(
            '''
                CREATE DATABASE "%s" WITH TEMPLATE "%s";
            ''' %
            (
                to_database,
                from_database
            )
        )
    elif raw_conn.engine.dialect.name == 'mysql':
        # Horribly slow implementation.
        create_database(raw_conn, to_database)
        for row in raw_conn.execute('SHOW TABLES in %s;' % from_database):
            raw_conn.execute('''
                CREATE TABLE %s.%s LIKE %s.%s
            ''' % (
                to_database,
                row[0],
                from_database,
                row[0]
            ))
            raw_conn.execute('ALTER TABLE %s.%s DISABLE KEYS' % (
                to_database,
                row[0]
            ))
            raw_conn.execute('''
                INSERT INTO %s.%s SELECT * FROM %s.%s
            ''' % (
                to_database,
                row[0],
                from_database,
                row[0]
            ))
    else:
        raise NotSupportedDatabase()


def database_exists(raw_conn, database):
    return sqlalchemy_utils.functions.database_exists(
        '%s%s' % (raw_conn.engine.url, database)
    )


def remove_database(raw_conn, database):
    terminate_database_connections(raw_conn, database)
    return sqlalchemy_utils.functions.drop_database(
        '%s%s' % (raw_conn.engine.url, database)
    )


def rename_database(raw_conn, from_database, to_database):
    if raw_conn.engine.dialect.name == 'postgresql':
        raw_conn.execute(
            '''
                ALTER DATABASE "%s" RENAME TO "%s"
            ''' %
            (
                from_database,
                to_database
            )
        )
    elif raw_conn.engine.dialect.name == 'mysql':
        create_database(raw_conn, to_database)
        for row in raw_conn.execute('SHOW TABLES in %s;' % from_database):
            raw_conn.execute('''
                RENAME TABLE %s.%s TO %s.%s;
            ''' % (
                from_database,
                row[0],
                to_database,
                row[0]
            ))
        remove_database(raw_conn, from_database)
    else:
        raise NotSupportedDatabase()


def list_of_databases(raw_conn):
    if raw_conn.engine.dialect.name == 'postgresql':
        return [
            row[0]
            for row in raw_conn.execute('''
                SELECT datname FROM pg_database
                WHERE datistemplate = false
            ''')
        ]
    elif raw_conn.engine.dialect.name == 'mysql':
        return [
            row[0]
            for row in raw_conn.execute('''SHOW DATABASES''')
        ]
    else:
        raise NotSupportedDatabase()

