from enum import Enum


class RepeatType(Enum):
    EVERY_DAY = 'Ежедневно'
    EVERY_WEEK = 'Еженедельно'
    EVERY_MONTH = 'Ежемесячно'
    EVERY_YEAR = 'Ежегодно'
    ONLY_DAY = 'Только сегодня'


class RepeatDays(Enum):
    MONDAY = 'Понедельник'
    TUESDAY = 'Вторник'
    WEDNESDAY = 'Среда'
    THURSDAY = 'Четверг'
    FRIDAY = 'Пятница'
    SATURDAY = 'Суббота'
    SUNDAY = 'Воскресенье'
    ALL_DAYS = 'Все дни'
