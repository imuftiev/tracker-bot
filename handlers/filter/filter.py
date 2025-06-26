from aiogram.filters import BaseFilter
from aiogram.types import Message

"""
    Фильтр для доступа к командам удаления и добавления только в личных чатах.
"""
class IsPrivate(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.chat.type == 'private'
