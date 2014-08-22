Stellar - Fast database snapshot and restore tool for development.
=======

Stellar allows you to quickly restore database when you are e.g. writing database migrations, switching branches or messing with SQL. PostgreSQL and MySQL are supported.

![Screenshot of Stellar terminal window](http://imgur.com/0fXXdcx.png)

Benchmarks
-------
Stellar is fast. It can restore database ~140 times faster than using the usual
pg_dump & pg_restore.

![Benchmarking database restore speed](http://imgur.com/Md1AHXa.png)

How it works
-------

Stellar works by storing copies of the database in the RDBMS (named as stellar_xxx_master and stellar_xxxx_slave). When restoring the database, Stellar simply renames the database making it lot faster than the usual SQL dump. However, Stellar uses lots of storage space so you probably don't want to mae too many snapshots or you will eventually run out of storage space.

Due to experimental nature of this tool, it is not recommended to use this in an enviroment where you can't afford possible data loss (eg. production)

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
