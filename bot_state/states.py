from aiogram.fsm.state import StatesGroup, State


class AddEventState(StatesGroup):
    adding_title = State()
    adding_description = State()
    adding_status = State()
    adding_priority = State()
    adding_created_at = State()
    adding_updated_at = State()
    adding_repeatable = State()
    adding_remind_at = State()
    adding_remind_date = State()
    adding_repeat_type = State()
    adding_chat_name = State()

    adding_privacy = State()
    adding_group = State()
    telegram_chat_id = State()
    user_id = State()


class UpdateEventState(StatesGroup):
    updating = State()
    updating_description = State()
    updating_status = State()
    updating_priority = State()


class RepeatableEventState(StatesGroup):
    adding_day = State()


class GroupLinkState(StatesGroup):
    attach_link = State()


class EventsListFilter(StatesGroup):
    events_list = State()
    events_priority_filter = State()
    events_status_filter = State()
