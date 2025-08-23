from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


menuCMDbuilder = dict()
menuCMDbuilder["main"] = InlineKeyboardBuilder([[
    InlineKeyboardButton(text="Ассортимент 📋", callback_data="items_cb"),
    InlineKeyboardButton(text="Настройки ⚙️", callback_data="settings_cb"),
    InlineKeyboardButton(text="Предпросмотр 📲️", callback_data="preview_cb"),
    InlineKeyboardButton(text="Статистика 📈", callback_data="statistics_cb"),
    InlineKeyboardButton(text="Информация ℹ️", callback_data="info_cb")
]])
menuCMDbuilder["main"].adjust(1)
menuCMDbuilder["items"] = InlineKeyboardBuilder([[
    InlineKeyboardButton(text="Текущий ассортимент 📃", callback_data="items_now_cb"),
    InlineKeyboardButton(text="Добавить новые товары ➕", callback_data="items_new_cb"),
    InlineKeyboardButton(text="Изменить существующие 🔄️", callback_data="items_edit_cb"),
    InlineKeyboardButton(text="Удалить всё 💀", callback_data="items_delete_cb"),
    InlineKeyboardButton(text="◀️ Назад", callback_data="items_back_cb")
]])
menuCMDbuilder["items"].adjust(1)
menuCMDbuilder["items_edit"] = InlineKeyboardBuilder([[
    InlineKeyboardButton(text="Изменить 🔁", callback_data="current_item_edit_cb"),
    InlineKeyboardButton(text="Удалить 🗑️", callback_data="current_item_delete_cb"),
    InlineKeyboardButton(text="Следующий ▶️", callback_data="current_item_skip_cb")
]])
menuCMDbuilder["items_edit"].adjust(1)
menuCMDbuilder["items_delete"] = InlineKeyboardBuilder([[
    InlineKeyboardButton(text="Да, хочу удалить!", callback_data="confirm_delete_item_cb"),
    InlineKeyboardButton(text="Нет, хочу оставить!", callback_data="deny_delete_item_cb")
]])
menuCMDbuilder["items_delete"].adjust(1)
menuCMDbuilder["settings"] = InlineKeyboardBuilder([[
    InlineKeyboardButton(text="Название 🆕", callback_data="settings_name_cb"),
    InlineKeyboardButton(text="Описание 🆒", callback_data="settings_description_cb"),
    InlineKeyboardButton(text="Логотип 🖼️", callback_data="settings_logo_cb"),
    InlineKeyboardButton(text="◀️ Назад", callback_data="settings_back_cb")
]])
menuCMDbuilder["settings"].adjust(1)
menuCMDbuilder["settings_logo"] = InlineKeyboardBuilder([[
    InlineKeyboardButton(text="Обнулить логотип 🛑", callback_data="settings_null_logo_cb")
]])

menuCMD = dict(zip(
    menuCMDbuilder.keys(),
    list(map(lambda s: s.as_markup(), menuCMDbuilder.values()))
))

skipLogoCMDbuilder = InlineKeyboardBuilder([[InlineKeyboardButton(text="Пропустить", callback_data="skip_cb")]])
skipLogoCMD = skipLogoCMDbuilder.as_markup()

accessCMDbuilder = InlineKeyboardBuilder([[
    InlineKeyboardButton(text="👁️‍🗨️ Просмотр пользователей", callback_data="access_monitor_cb"),
    InlineKeyboardButton(text="➕ Добавить пользователя", callback_data="access_add_cb"),
    InlineKeyboardButton(text="➖ Удалить пользователя", callback_data="access_remove_cb")
]])
accessCMDbuilder.adjust(1)
accessCMD = accessCMDbuilder.as_markup()

adCMDbuilder = dict()
adCMDbuilder["phase1"] = InlineKeyboardBuilder([[
    InlineKeyboardButton(text="Просмотр 👁", callback_data="ad_continue_cb")
]])
adCMDbuilder["phase2"] = InlineKeyboardBuilder([[
    InlineKeyboardButton(text="Отмена ❌", callback_data="ad_cancel_cb"),
    InlineKeyboardButton(text="Отправить на модерацию ✨", callback_data="ad_send_to_moderators_cb")
]])
adCMDbuilder["phase2"].adjust(1)

adCMD = dict(zip(
    adCMDbuilder.keys(),
    list(map(lambda s: s.as_markup(), adCMDbuilder.values()))
))
