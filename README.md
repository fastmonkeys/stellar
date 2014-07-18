Stellar - Lightning fast database snapshots for development
=======

Basic usage:

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
