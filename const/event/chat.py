from enum import Enum


class Chat(Enum):
    GROUP = 'GROUP'
    PRIVATE = 'PRIVATE'

class ChatName(Enum):
    PERSONAL = 'Личный'
    GROUP = 'Группа'