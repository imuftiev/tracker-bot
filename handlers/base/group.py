from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram import F

from bot_state.states import AddEventState

router = Router()

# @router.callback_query(F.data, AddEventState.adding_group)
# async def attach_group(callback : types.CallbackQuery ,state : FSMContext):
