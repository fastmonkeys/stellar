import logging

import sqlalchemy_utils
import sqlalchemy as sa

logger = logging.getLogger(__name__)


SUPPORTED_DIALECTS = ("postgresql", "mysql")


class NotSupportedDatabase(Exception):
    pass


def get_engine_url(raw_conn, database):
    url = str(raw_conn.engine.url)
    if url.count("/") == 3 and url.endswith("/"):
        return "%s%s" % (url, database)
    else:
        if not url.endswith("/"):
            url += "/"
        return "%s/%s" % ("/".join(url.split("/")[0:-2]), database)


def terminate_database_connections(raw_conn, database):
    logger.debug("terminate_database_connections(%r)", database)
    if raw_conn.engine.dialect.name == "postgresql":
        raw_conn.execute(
            sa.text(
                """
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE
                        pg_stat_activity.datname = :database AND
                        pid <> pg_backend_pid();
                """
            ),
            {"database": database},
        )
    else:
        raise NotImplementedError()


def create_database(raw_conn, database, template="template0"):
    logger.debug("create_database(%r)", database)
    return sqlalchemy_utils.functions.create_database(
        get_engine_url(raw_conn, database),
        template=template,
    )


def copy_database(raw_conn, from_database, to_database):
    logger.debug("copy_database(%r, %r)", from_database, to_database)
    terminate_database_connections(raw_conn, from_database)

    if raw_conn.engine.dialect.name == "postgresql":
        create_database(raw_conn, to_database, from_database)
    elif raw_conn.engine.dialect.name == "mysql":
        # Horribly slow implementation.
        create_database(raw_conn, to_database)
        for row in raw_conn.execute(sa.text("SHOW TABLES in %s;" % from_database)):
            raw_conn.execute(
                sa.text(
                    """
                        CREATE TABLE %s.%s LIKE %s.%s
                    """
                    % (to_database, row[0], from_database, row[0])
                )
            )
            raw_conn.execute(
                sa.text("ALTER TABLE %s.%s DISABLE KEYS" % (to_database, row[0]))
            )
            raw_conn.execute(
                sa.text(
                    """
                INSERT INTO %s.%s SELECT * FROM %s.%s
            """
                    % (to_database, row[0], from_database, row[0])
                )
            )
            raw_conn.execute(
                sa.text("ALTER TABLE %s.%s ENABLE KEYS" % (to_database, row[0]))
            )
    else:
        raise NotSupportedDatabase()


def database_exists(raw_conn, database):
    logger.debug("database_exists(%r)", database)
    return sqlalchemy_utils.functions.database_exists(
        get_engine_url(raw_conn, database)
    )


def remove_database(raw_conn, database):
    logger.debug("remove_database(%r)", database)
    terminate_database_connections(raw_conn, database)
    return sqlalchemy_utils.functions.drop_database(get_engine_url(raw_conn, database))


def rename_database(raw_conn, from_database, to_database):
    logger.debug("rename_database(%r, %r)", from_database, to_database)
    terminate_database_connections(raw_conn, from_database)
    if raw_conn.engine.dialect.name == "postgresql":
        raw_conn.execute(
            sa.text(
                """
                    ALTER DATABASE "%s" RENAME TO "%s"
                """
                % (from_database, to_database)
            )
        )
    elif raw_conn.engine.dialect.name == "mysql":
        create_database(raw_conn, to_database)
        for row in raw_conn.execute(sa.text("SHOW TABLES in %s;" % from_database)):
            raw_conn.execute(
                sa.text(
                    """'
                        RENAME TABLE %s.%s TO %s.%s;
                    """
                    % (from_database, row[0], to_database, row[0])
                )
            )
        remove_database(raw_conn, from_database)
    else:
        raise NotSupportedDatabase()


def list_of_databases(raw_conn):
    logger.debug("list_of_databases()")
    if raw_conn.engine.dialect.name == "postgresql":
        return [
            row[0]
            for row in raw_conn.execute(
                sa.text(
                    """
                    SELECT datname FROM pg_database
                    WHERE datistemplate = false
                """
                )
            )
        ]
    elif raw_conn.engine.dialect.name == "mysql":
        return [row[0] for row in raw_conn.execute(sa.text("""SHOW DATABASES"""))]
    else:
        raise NotSupportedDatabase()
