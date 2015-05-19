Stellar - Fast database snapshot and restore tool for development.
=======

[![Build Status](https://travis-ci.org/fastmonkeys/stellar.svg?branch=master)](https://travis-ci.org/fastmonkeys/stellar)&nbsp;
![](http://img.shields.io/pypi/dm/stellar.svg)&nbsp;
![](http://img.shields.io/pypi/v/stellar.svg)


Stellar allows you to quickly restore database when you are e.g. writing database migrations, switching branches or messing with SQL. PostgreSQL and MySQL (partially) are supported.

![Screenshot of Stellar terminal window](http://imgur.com/0fXXdcx.png)


Benchmarks
-------
Stellar is fast. It can restore a database ~140 times faster than using the usual
pg_dump & pg_restore.

![Benchmarking database restore speed](http://imgur.com/Md1AHXa.png)

How it works
-------

Stellar works by storing copies of the database in the RDBMS (named as stellar_xxx_master and stellar_xxxx_slave). When restoring the database, Stellar simply renames the database making it lot faster than the usual SQL dump. However, Stellar uses lots of storage space so you probably don't want to make too many snapshots or you will eventually run out of storage space.

**Warning: Please don't use Stellar if you can't afford data loss.** It's great for developing but not meant for production.

How to get started
-------

You can install Stellar with `pip`.

```$ pip install stellar```

After that, you should go to your project folder and initialize Stellar settings. Stellar initialization wizard will help you with that.

```$ stellar init```

Stellar settings are saved as 'stellar.yaml' so you probably want to add that to your `.gitignore`.

```$ echo stellar.yaml >> .gitignore```

Done! :dancers:


How to take a snapshot
-------

```$ stellar snapshot SNAPSHOT_NAME```

How to restore from a snapshot
-------

```$ stellar restore SNAPSHOT_NAME```

Common issues
-------

````
sqlalchemy.exc.OperationalError: (OperationalError) (1044, u"Access denied for user 'my_db_username'@'localhost' to database 'stellar_data'") "CREATE DATABASE stellar_data CHARACTER SET = 'utf8'" ()
`````

Make sure you have the rights to create new databases. See [Issue 10](https://github.com/fastmonkeys/stellar/issues/10) for discussion

If you are using PostreSQL, make sure you have a database that is named the same as the unix username. You can test this by running just `psql`. (See [issue #44](https://github.com/fastmonkeys/stellar/issues/44) for details)
