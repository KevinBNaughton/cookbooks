# Run the Flask server

```shell
uv run -m flask --app app run
```

## MongoDB stuff

Use the MongoDB Compass App on Mac or Linux for a nice GUI.

[Mac Install](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-os-x/)

Start MongoDB on Mac M1. Refer to above for other platforms.

```shell
mongod --config /opt/homebrew/etc/mongod.conf --fork
```

Kill all the `mongod` database processes.

```shell
pkill mongod
```

### Migrate DB Between Machines

If using MacOs anywhere, use
[GNU tar](https://superuser.com/questions/318809/linux-os-x-tar-incompatibility-tarballs-created-on-os-x-give-errors-when-unt)
instead of BSD tar.

```shell
# dumps your MongoDB database into dump/
mongodump --db your_database
# tar it
tar -czvf your_database.tgz dump/
# scp it
scp your_database.tgz instance:~/your_database.tgz
# on the new machine, untar
tar -xvf your_database.tgz
# Then restore your MongoDB database into a specified DB name
mongorestore --db your_database_name dump/your_database_name
```
