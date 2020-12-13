
import typing
from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from config import ACL


class AclAdminFilter(BoundFilter):
    """
    Check if message is sent by Admin from ACL
    """
    key = 'chat_id'

    def __init__(self, message: types.Message):

        self.ACL = ACL

    def check(self, message: types.Message) -> bool:
        return message.from_user.id in self.ACL
