Stellar - Fast database snapshots for development. It's like Git for databases.
=======

![Screenshot of Stellar terminal window](http://imgur.com/0fXXdcx.png)

Stellar allows you to quickly restore database when you are e.g. writing database migrations, switching branches or messing with SQL. PostreSQL and MySQL are supported.


```
> stellar init
Please enter project name (ex. myproject): my_project
Please enter database url (ex. postgresql://localhost:5432/): postgresql://localhost:5432/
Please enter project database name (ex. myproject): my_project_database
Wrote stellar.yaml

> stellar snapshot base
Snapshotting database my_project_database
> stellar list
base a minute ago ago
> stellar restore base
Restore complete.
```
