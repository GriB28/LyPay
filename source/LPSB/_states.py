from aiogram.fsm.state import StatesGroup, State


class MenuFSM(StatesGroup):
    MENU = State()
    ITEMS_NEW = State()
    ITEMS_DELETE = State()
    ITEMS_EDIT = State()
    ITEMS_WAIT_FOR_EDIT = State()
    SETTINGS_NAME = State()
    SETTINGS_DESCRIPTION = State()
    SETTINGS_LOGO = State()
    STATISTICS = State()
    HELP = State()


class RegistrationFSM(StatesGroup):
    CHECK_CODE = State()
    START = State()
    NAME = State()
    DESCRIPTION = State()
    LOGO = State()
    END = State()


class AccessFSM(StatesGroup):
    MENU = State()
    ADD_PICK = State()
    ADD_CONFIRM = State()
    REMOVE = State()
    REMOVE_PICK = State()
    REMOVE_CONFIRM = State()


class AdFSM(StatesGroup):
    WAITING = State()
    CONFIRM = State()


class AdAdminFSM(StatesGroup):
    SEND_ID = State()
    TEXT = State()
    SEND_CONFIRM = State()
    APPROVE_ID = State()
    APPROVE_CONFIRM = State()
