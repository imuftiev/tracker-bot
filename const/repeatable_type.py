from enum import Enum


class RepeatType(Enum):
    EVERY_DAY = 'Ежедневно'
    EVERY_WEEK = 'Еженедельно'
    EVERY_MONTH = 'Ежемесячно'
    EVERY_YEAR = 'Ежегодно'
    ONLY_DAY = 'Только сегодня'
    IN_PARTICULAR_DAY = 'Определенный день'

class RepeatDays(Enum):
    ALL_DAYS = 'Все дни'
    EXACT_DAY = 'Определенный день'