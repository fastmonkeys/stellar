Stellar - Fast database snapshots for development. It's like Git for databases.
=======

Stellar allows you to quickly restore database when you are e.g. writing database migrations, switching branches or messing with SQL. PostreSQL and MySQL are supported.

![Screenshot of Stellar terminal window](http://imgur.com/0fXXdcx.png)

Benchmarks
-------
Stellar is fast. It can restore database ~140 times faster than using the usual
pg_dump & pg_restore.

![Benchmarking database restore speed](http://imgur.com/Md1AHXa.png)


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
