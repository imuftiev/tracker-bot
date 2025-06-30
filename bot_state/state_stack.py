import logging

from aiogram.fsm.context import FSMContext


async def push_state(state: FSMContext, new_state):
    try:
        logging.info("Calling push_state")
        data = await state.get_data()
        history = data.get("history", [])
        current_state = await state.get_state()
        logging.info(f"Current state: {current_state}")
        if current_state:
            history.append(current_state)
        await state.update_data(history=history)
        await state.set_state(new_state)
    except Exception as e:
        logging.error(e)
