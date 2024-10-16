from aiogram.fsm.state import StatesGroup, State


class Ongoing(StatesGroup):
    add = State()
    delete = State()
