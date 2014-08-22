import argparse
import sys
import os
from datetime import datetime
from time import sleep

import humanize
import click
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

from app import Stellar, __version__
from config import InvalidConfig, MissingConfig
from operations import database_exists, list_of_databases, SUPPORTED_DIALECTS


@click.group()
def stellar():
    """Fast database snapshots for development. It's like Git for databases."""
    pass

@stellar.command()
def version():
    """Shows version number"""
    print "Stellar %s" % __version__


@stellar.command()
def gc():
    """Deletes old stellar tables that are not used anymore"""
    def after_delete(database):
        print "Deleted table %s" % database

    app = Stellar()
    app.delete_orphan_snapshots(after_delete)


@stellar.command()
@click.argument('name', required=False)
def snapshot(name):
    """Takes a snapshot of the database"""
    app = Stellar()
    name = name or app.default_snapshot_name

    if app.get_snapshot(name):
        print "Snapshot with name %s already exists" % name
        sys.exit(1)
    else:
        def before_copy(table_name):
            print "Snapshotting database %s" % table_name
        app.create_snapshot(name, before_copy=before_copy)


@stellar.command()
def list():
    """Returns a list of snapshots"""
    snapshots = Stellar().get_snapshots()

    print '\n'.join(
        '%s: %s' % (
            s.snapshot_name,
            humanize.naturaltime(datetime.utcnow() - s.created_at)
        )
        for s in snapshots
    )


@stellar.command()
@click.argument('name', required=False)
def restore(name):
    """Restores the database from a snapshot"""
    app = Stellar()

    if not name:
        snapshot = app.get_latest_snapshot()
        if not snapshot:
            print (
                "Couldn't find any snapshots for project %s" %
                self.config['project_name']
            )
            sys.exit(1)
    else:
        snapshot = app.get_snapshot(name)
        if not snapshot:
            print (
                "Couldn't find snapshot with name %s.\n"
                "You can list snapshots with 'stellar list'" % name
            )
            sys.exit(1)

    # Check if slaves are ready
    if not snapshot.slaves_ready:
        if app.is_copy_process_running(snapshot):
            sys.stdout.write(
                'Waiting for background process(%s) to finish' %
                snapshot.worker_pid
            )
            sys.stdout.flush()
            while not snapshot.slaves_ready:
                sys.stdout.write('.')
                sys.stdout.flush()
                sleep(1)
                app.db.session.refresh(snapshot)
            print ''
        else:
            print 'Background process missing, doing slow restore.'
            app.inline_slave_copy(snapshot)

    app.restore(snapshot)
    print "Restore complete."


@stellar.command()
@click.argument('name')
def remove(name):
    """Removes a snapshot"""
    app = Stellar()

    snapshot = app.get_snapshot(name)
    if not snapshot:
        print "Couldn't find snapshot %s" % name
        sys.exit(1)

    print "Deleting snapshot %s" % name
    app.remove_snapshot(snapshot)
    print "Deleted"


@stellar.command()
@click.argument('old_name')
@click.argument('new_name')
def rename(old_name, new_name):
    """Renames a snapshot"""
    app = Stellar()

    snapshot = app.get_snapshot(old_name)
    if not snapshot:
        print "Couldn't find snapshot %s" % old_name
        sys.exit(1)

    new_snapshot = app.get_snapshot(new_name)
    if new_snapshot:
        print "Snapshot with name %s already exists" % new_name
        sys.exit(1)

    app.rename_snapshot(snapshot, new_name)
    print "Renamed snapshot %s to %s" % (old_name, new_name)


@stellar.command()
def init():
    """Initializes Stellar configuration."""
    while True:
        url = click.prompt(
            "Please enter the url for your database.\n\n"
            "For example:\n"
            "PostreSQL: postgresql://localhost:5432/\n"
            "MySQL: mysql+pymysql://root@localhost/"
        )
        if not url.endswith('/'):
            url = url + '/'

        engine = create_engine(url, echo=False)
        try:
            conn = engine.connect()
        except OperationalError:
            print "Could not connect to database: %s" % url
            print "Make sure database process is running and try again."
            print
        else:
            break

    if engine.dialect.name not in SUPPORTED_DIALECTS:
        print "Your engine dialect %s is not supported." % (
            engine.dialect.name
        )
        print "Supported dialects: %s" % (
            ', '.join(SUPPORTED_DIALECTS)
        )

    while True:
        click.echo("You have the following databases: %s" % ', '.join([
            db for db in list_of_databases(conn)
            if not db.startswith('stellar_')
        ]))

        db_name = click.prompt(
            "Please enter the name of the database (eg. projectdb)"
        )
        if database_exists(conn, db_name):
            break
        else:
            print "Could not find database %s" % db_name
            print

    name = click.prompt(
        'Please enter your project name (used internally, eg. %s)' % db_name,
        default=db_name
    )

    with open('stellar.yaml', 'w') as project_file:
        project_file.write(
            """
project_name: '%(name)s'
tracked_databases: ['%(db_name)s']
url: '%(url)s'
stellar_url: '%(url)sstellar_data'
            """.strip() %
            {
                'name': name,
                'url': url,
                'db_name': db_name
            }
        )

    print "Wrote stellar.yaml"
    print
    if engine.dialect.name == 'mysql':
        print "Warning: MySQL support is still in beta."
    print "Tip: You probably want to take a snapshot: stellar snapshot"


def main():
    try:
        stellar()
    except MissingConfig:
        print "You don't have stellar.yaml configuration yet."
        print "Initialize it by running: stellar init"
        sys.exit(1)
    except InvalidConfig, e:
        print "Your stellar.yaml configuration is wrong: %s" % e.message
        sys.exit(1)
    except ImportError, e:
        libraries = {
            'psycopg2': 'PostreSQL',
            'pymysql': 'MySQL',
        }
        for library, name in libraries.items():
            if str(e) == 'No module named %s' % library:
                print "Python library %s is required for %s support." % (
                    library,
                    name
                )
                print "You can install it with pip:"
                print "pip install %s" % library
                sys.exit(1)
        raise

if __name__ == '__main__':
    main()
