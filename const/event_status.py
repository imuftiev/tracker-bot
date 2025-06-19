from enum import Enum


class EventStatus(Enum):
    TO_DO = 'Выполнить'
    PROCESSING = 'Обрабатывается'
    DONE = 'Выполнено'
