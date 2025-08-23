from aiogram.fsm.state import StatesGroup, State


class TransferFSM(StatesGroup):
    STORE = State()
    INPUT = State()
    CONFIRM1 = State()
    CONFIRM2 = State()


'''
class TicketFSM(StatesGroup):
    BUY = State()
'''