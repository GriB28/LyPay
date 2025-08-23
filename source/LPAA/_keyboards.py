from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


infoCMDbuilder_user = InlineKeyboardBuilder([[
    InlineKeyboardButton(text="ID", callback_data="user_ID_"),
    InlineKeyboardButton(text="тег", callback_data="user_TAG_"),
    InlineKeyboardButton(text="имя", callback_data="user_NAME_"),
    InlineKeyboardButton(text="почта", callback_data="user_EMAIL_"),
    InlineKeyboardButton(text="переводы", callback_data="user_TRANSACTION_")
]])
infoCMDbuilder_user.adjust(2)
infoCMD_user = infoCMDbuilder_user.as_markup()

infoCMDbuilder_store = InlineKeyboardBuilder([[
    InlineKeyboardButton(text="ID", callback_data="store_ID_"),
    InlineKeyboardButton(text="название", callback_data="store_NAME_"),
    InlineKeyboardButton(text="описание", callback_data="store_DESC_"),
    InlineKeyboardButton(text="владелец", callback_data="store_HOST_"),
    InlineKeyboardButton(text="переводы", callback_data="store_TRANSACTION_")
]])
infoCMDbuilder_store.adjust(2)
infoCMD_store = infoCMDbuilder_store.as_markup()

infoCMDbuilder_cheque = InlineKeyboardBuilder([[
    InlineKeyboardButton(text="ID", callback_data="cheque_ID_"),
    InlineKeyboardButton(text="магазин", callback_data="cheque_STORE_"),
    InlineKeyboardButton(text="покупатель", callback_data="cheque_CUSTOMER_")
]])
infoCMDbuilder_cheque.adjust(2)
infoCMD_cheque = infoCMDbuilder_cheque.as_markup()

whitelistCMDbuilder = InlineKeyboardBuilder([[
    InlineKeyboardButton(text="MAIN", callback_data="main_cb"),
    InlineKeyboardButton(text="LPSB", callback_data="lpsb_cb")
]])
whitelistCMD = whitelistCMDbuilder.as_markup()
