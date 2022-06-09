from src.db.Models import User, Auction, Bet, BaseModel
from src.Utils import database, manager

models = [User, Auction, Bet]


def create_tables():
    database.create_tables(models)


def clear_tables():
    database.drop_tables(models)


async def make_admin(username: str):
    user = await manager.get(User, User.username == username)

    user.is_superuser = True
    user.save()


def make_admin_sync(username: str):
    user = User.get(User.username == username)

    user.is_superuser = True
    user.save()
