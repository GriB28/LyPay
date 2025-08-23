from aiogram.fsm.state import StatesGroup, State


class RegisterFSM(StatesGroup):
    STATE0 = State()
    EMAIL = State()
    CODE = State()
    GUEST_NAME_INPUT = State()
    LINK = State()
    CONFIRM_LINKING = State()


class StoreFSM(StatesGroup):
    ID = State()
    ITEM = State()
    MULTIPLIER = State()
    CONFIRM = State()


class TransferFSM(StatesGroup):
    USER = State()
    MODE = State()
    CONFIRM1 = State()
    INPUT = State()
    CONFIRM2 = State()


class CouponFSM(StatesGroup):
    ID = State()
    CONFIRM = State()
