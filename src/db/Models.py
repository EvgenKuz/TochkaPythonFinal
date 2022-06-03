from peewee import Model, CharField, BooleanField, UUIDField, \
    ForeignKeyField, DecimalField, TextField, DateTimeField
from src.Utils import database


class BaseModel(Model):
    class Meta:
        database = database


class User(BaseModel):
    username = CharField(primary_key=True, unique=True)
    email = CharField(unique=True)
    password = CharField()
    is_superuser = BooleanField(default=False)


class Auction(BaseModel):
    id = UUIDField(primary_key=True, unique=True)
    name = CharField()
    user = ForeignKeyField(User, backref="auctions")
    staring_price = DecimalField(decimal_places=2, auto_round=True)
    picture = CharField()
    allowed = BooleanField(default=True)
    description = TextField()
    end_of_auction = DateTimeField()


class Bet(BaseModel):
    auction = ForeignKeyField(Auction, field="id", backref="bets")
    user = ForeignKeyField(User, field="username", backref="bets")
    bet = DecimalField(decimal_places=2, auto_round=True)

