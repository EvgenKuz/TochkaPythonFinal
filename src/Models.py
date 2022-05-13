from peewee import Model, CharField, BooleanField
from src.Utils import database


class BaseModel(Model):
    class Meta:
        database = database


class User(BaseModel):
    username = CharField(primary_key=True, unique=True)
    email = CharField(unique=True)
    password = CharField()
    is_superuser = BooleanField(default=False)


def create_tables():
    database.create_tables([User])
