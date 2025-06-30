from enum import Enum


class InlineButtonType(Enum):
    CANCEL = 'CANCEL'
    RETURN = 'RETURN'
    CONFIRM = 'CONFIRM'


class RepeatTypeInlineButton(Enum):
    CONFIRM_MONTH = 'CONFIRM_MONTH'
