from enum import Enum


class Status(Enum):
    TO_DO = 'Выполнить'
    PROCESSING = 'Обрабатывается'
    DONE = 'Выполнено'
