from aiogram.fsm.state import StatesGroup, State

class RateState(StatesGroup):
    waiting_forward = State()
    waiting_amount = State()

class PunishState(StatesGroup):
    waiting_forward = State()

class CourtState(StatesGroup):
    waiting_forward = State()
