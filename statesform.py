from aiogram.fsm.state import StatesGroup, State


class StepsForm(StatesGroup):
    GET_NAME = State()
    GET_ITEMS = State()
    INSERTION_FINISHED = State()
    GET_PERSON1 = State()
    GET_PERSON2 = State()
    GET_PERSON3 = State()
    REMOVE_ITEMS = State()
