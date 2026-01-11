from aiogram import Router
from aiogram.fsm.state import State, StatesGroup


class Mode(StatesGroup):
    choosing_mode = State()
    transformation = State()
    translating = State()
    learn = State()
    waiting_for_target_language = State()



