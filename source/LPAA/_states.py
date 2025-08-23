from aiogram.fsm.state import StatesGroup, State


class DepositFSM(StatesGroup):
    ZERO = State()
    DEPOSIT_QR = State()
    DEPOSIT_AMOUNT = State()
    CONFIRM = State()


class StoreRegisterFSM(StatesGroup):
    EMAIL = State()


class HighDepositFSM(StatesGroup):
    DEPOSIT_QR = State()
    DEPOSIT_AMOUNT = State()
    CONFIRM = State()


class InfoFSM(StatesGroup):
    INFO = State()
    USER_ID = State()
    USER_NAME = State()
    USER_EMAIL = State()
    USER_TAG = State()
    TRANSACTION = State()
    STORE_ID = State()
    STORE_NAME = State()
    STORE_DESC = State()
    STORE_HOST = State()
    CHEQUE_ID = State()
    CHEQUE_STORE = State()
    CHEQUE_CUST = State()


class AnnounceFSM(StatesGroup):
    PREPARING = State()
    PICKING = State()


class WhitelistFSM(StatesGroup):
    BOT = State()
    USER = State()
    CONFIRM = State()


class BanFSM(StatesGroup):
    ID = State()
    CONFIRM = State()


class PardonFSM(StatesGroup):
    ID = State()
    CONFIRM = State()


class AuctionFSM(StatesGroup):
    NAME = State()
    PRICE = State()
    AUC_ID = State()
