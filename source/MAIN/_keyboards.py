from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, ReplyKeyboardBuilder, KeyboardButton
from scripts import lpsql
from data.config import VALUTA
keyboard_db_shortcut = lpsql.DataBase("lypay_database.db", lpsql.Tables.MAIN)

startCMDbuilder = InlineKeyboardBuilder([[
    InlineKeyboardButton(text="Официальный канал Ярмарки", url="https://t.me/fairL2SH")
]])
startCMD = startCMDbuilder.as_markup()

registerCMDbuilder = InlineKeyboardBuilder([[
    InlineKeyboardButton(text="Привязать аккаунт Расписания Л2Ш", callback_data="register_linking_cb"),
    InlineKeyboardButton(text="По почте", callback_data="register_main_cb"),
    InlineKeyboardButton(text="Гостевой доступ", callback_data="register_guest_cb")
]])
registerCMDbuilder.adjust(1)
registerCMD = registerCMDbuilder.as_markup()

registerLinkCMDbuilder = InlineKeyboardBuilder([[
    InlineKeyboardButton(text="Всё верно ✅", callback_data="register_link_confirm_cb"),
    InlineKeyboardButton(text="◀️ Назад", callback_data="register_link_back_cb")
]])
registerLinkCMDbuilder.adjust(1)
registerLinkCMD = registerLinkCMDbuilder.as_markup()

transferCMDbuilder = InlineKeyboardBuilder([[
    InlineKeyboardButton(text="Тег", callback_data="transfer_tag_cb"),
    InlineKeyboardButton(text="Фамилия", callback_data="transfer_name_cb"),
    InlineKeyboardButton(text="QR-код", callback_data="transfer_qr_cb")
]])
transferCMDbuilder.adjust(3)
transferCMD = transferCMDbuilder.as_markup()

storeCMDbuilder = InlineKeyboardBuilder([[
    InlineKeyboardButton(text="Отменить покупку", callback_data="store_cancel_cb"),
    InlineKeyboardButton(text="Продолжить выбор товаров", callback_data="store_continue_cb"),
    InlineKeyboardButton(text="Закончить покупку", callback_data="store_confirm_cb")
]])
storeCMDbuilder.adjust(1)
storeCMD = storeCMDbuilder.as_markup()

promoCMDbuilder = InlineKeyboardBuilder([[
    InlineKeyboardButton(text="Активировать", callback_data="promo_activate_cb")
]])
promoCMD = promoCMDbuilder.as_markup()


def update_keyboard(uid: int | None = None, cancel_mode: bool = False) -> ReplyKeyboardMarkup | ReplyKeyboardRemove:
    if uid is None:
        return ReplyKeyboardRemove()
    user_db = keyboard_db_shortcut.search("users", "ID", uid)
    if user_db is None:
        return ReplyKeyboardRemove()

    if cancel_mode:
        keyboard = ReplyKeyboardBuilder([[
            KeyboardButton(text="↩️ Отмена")
        ]])
    else:
        if user_db["balance"] >= VALUTA.MONEYBAG_CRITERION:
            keyboard = ReplyKeyboardBuilder([[
                KeyboardButton(text="💳 Пополнить баланс"),
                KeyboardButton(text="🛍 Покупка"),
                KeyboardButton(text="📤 Перевод пользователю"),
                KeyboardButton(text="⚙️ Авторы"),
                KeyboardButton(text="😱 Баланс")
            ]])
        else:
            keyboard = ReplyKeyboardBuilder([[
                KeyboardButton(text="💳 Пополнить баланс"),
                KeyboardButton(text="🛍 Покупка"),
                KeyboardButton(text="📤 Перевод пользователю"),
                KeyboardButton(text="⚙️ Авторы"),
                KeyboardButton(text="💰 Баланс")
            ]])
        keyboard.adjust(1, 1, 1, 2)

    return keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True, input_field_placeholder="Главное меню")
