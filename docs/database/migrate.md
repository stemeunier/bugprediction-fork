# Migrate a database

*bugprediction* uses [alembic](https://alembic.sqlalchemy.org/en/latest/index.html) to migrate database schema to the latest DB model. **Please note that the result of the migration depends on the DB engine**. It means that some migration scripts may not work with SQLite (and that you might need to upgrade the schema manually).

# Instructions

1. Install alembic
2. Edit `alembic.ini` configuration file and especially the variable `sqlalchemy.url` which should have the same value than the one in the `.env` file.
3. Execute alembic commands in order to manage the schema

Example:

    $ alembic upgrade head
    INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
    INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
    INFO  [alembic.runtime.migration] Running upgrade  -> a3139821d248, upgrade metric table

See [alembic migration script documentation](https://alembic.sqlalchemy.org/en/latest/tutorial.html#create-a-migration-script) for more commands.
