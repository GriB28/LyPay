from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


accessCMDbuilder = InlineKeyboardBuilder([[
    InlineKeyboardButton(text="👁️‍🗨️ Просмотр пользователей", callback_data="access_monitor_cb"),
    InlineKeyboardButton(text="➕ Добавить пользователя", callback_data="access_add_cb"),
    InlineKeyboardButton(text="➖ Удалить пользователя", callback_data="access_remove_cb")
]])
accessCMDbuilder.adjust(1)
accessCMD = accessCMDbuilder.as_markup()

ticketCMDbuilder = InlineKeyboardBuilder([[
    InlineKeyboardButton(text="🪙 Купить", callback_data="ticket_buy_cb"),
    InlineKeyboardButton(text="❌ Отмена", callback_data="ticket_cancel_cb")
]])
ticketCMDbuilder.adjust(1)
ticketCMD = ticketCMDbuilder.as_markup()
