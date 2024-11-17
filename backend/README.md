## Run the Flask server

```shell
uv run -m flask --app app run
```

## MongoDB stuff

Use the MongoDB Compass App on Mac or Linux for a nice GUI.

https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-os-x/

Start MongoDB on Mac M1. Refer to above for other platforms.

```shell
mongod --config /opt/homebrew/etc/mongod.conf --fork
```

Kill all the `mongod` database processes.

```shell
pkill mongod
```
