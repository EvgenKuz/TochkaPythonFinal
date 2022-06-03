import peewee

from src.db.Models import User
from passlib.hash import sha256_crypt
from src.Utils import manager
from aiohttp_security import AbstractAuthorizationPolicy


class AuthorizationPolicy(AbstractAuthorizationPolicy):

    async def authorized_userid(self, identity: str):

        is_in_db = await manager.get(User, User.username == identity)

        if is_in_db:
            return identity
        return None

    async def permits(self, identity: str, permission: str, context=None):
        if identity is None:
            return False

        if permission == "public":
            return True
        is_admin = (await manager.get(User, User.username == identity)).is_superuser

        return is_admin


async def check_credentials(login: str, password: str) -> bool:
    try:
        user: User = await manager.get(User.select(User.password)
                                       .where(User.username == login))
    except peewee.DoesNotExist:
        return False
    return sha256_crypt.verify(password, user.password)

