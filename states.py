from aiogram.fsm.state import StatesGroup, State


class Ongoing(StatesGroup):
    add = State()
    delete = State()


class Timezone(StatesGroup):
    set = State()


class Sync(StatesGroup):
    shikimori = State()
