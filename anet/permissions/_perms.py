from ._base import AbstractPermission
from anet.api.user.models import UserStatus

__all__ = ('Admin', 'Staff', 'Simple')


class Admin(AbstractPermission):
    perms = [st.name for st in UserStatus]


class Staff(AbstractPermission):
    perms = [UserStatus.STAFF.name, UserStatus.SIMPLE.name]


class Simple(AbstractPermission):
    perms = [UserStatus.SIMPLE.name]
