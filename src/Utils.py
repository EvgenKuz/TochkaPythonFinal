import asyncio
import os

from peewee_async import PostgresqlDatabase, Manager

database = PostgresqlDatabase(os.getenv("APP_DB_NAME"), host="postgres",
                              user=os.getenv("APP_DB_USER"), password=os.getenv("APP_DB_PASS"))
manager = Manager(database)
