from os import getcwd


class VALUTA:
    NAME = ['Тугрик', 'Тугрика', 'Тугрик', 'Тугрику', 'Тугриком', 'Тугрике', 'Тугрики', 'Тугриков']
    COURSE = 1 / 1  # тугрик / рубль
    SHORT = 'Тгр.'
    MANUAL_REDACT_m = """
Администратор списал с Вашего счёта {amount} %s
Если это произошло незапланированно, обратитесь к организатору.
""" % SHORT
    MANUAL_REDACT_p = """
Администратор зачислил Вам на счёт {amount} %s
Если это произошло незапланированно, обратитесь к организатору.
""" % SHORT
    MANUAL_REDACT_AUC = """
Администратор списал {amount} %s за покупку лота Аукциона.
Если это произошло незапланированно, обратитесь к организатору.
""" % SHORT
    MONEYBAG_CRITERION = 30000


class COMMANDS:
    MAIN = [
        ('/start',      'Старт'),
        # ('/store',      'Оплатить покупку'),
        # ('/deposit',    'Положить %s на счёт' % VALUTA.NAME[6]),
        ('/cancel',     'Отменить текущее действие'),
        # ('/balance',    'Баланс'),
        # ('/transfer',   'Перевести %s пользователю' % VALUTA.NAME[6]),
        # ('/get_qr',     '(hidden) Получить личный QR'),
        # ('/delete',     '(hidden) Удаление аккаунта'),
        # ('/credits',    'Об авторах'),
        ('/help',       'Руководство')
    ]
    LPAA = [
        ('/cancel',     'Отменить текущее действие'),
        ('/deposit',    'Положить %s на счёт' % VALUTA.NAME[6])
        # ('/info',       'Информационный запрос'),
        # ('/machine',    'Состояние сервера'),
        # ('/whitelist',  'Открыть пользователю доступ'),
        # ('/announce_main', '[HIGH] Отправить сообщение в MAIN'),
        # ('/announce_lpsb', '[HIGH] Отправить сообщение в LPSB'),
        # ('/ban',        '[HIGH] Блокировка пользователя'),
        # ('/pardon',     '[HIGH] Разблокировка пользователя')
    ]
    LPSB = [
        ('/start',  'Старт'),
        ('/menu',   'Главное меню'),
        ('/cancel', 'Отменить текущее действие'),
        ('/access', 'Настройки доступа'),
        ('/ad',     'Опубликовать рекламу')
    ]
    AUC = [
        ('/start',      'Старт'),
        ('/balance',    'Баланс магазина'),
        ('/cancel',     'Отменить текущее действие'),
        ('/transfer',   'Перевести деньги другому магазину'),
        # ('/ticket',     'Купить билет беспроигрышной лотереи'),
        ('/access',     'Настройки доступа')
    ]
    SRV = [
        ('/start',      'Старт')
    ]


class NAMES:
    MAIN = [
        ("LyPay — Банк Ярмарки Л2Ш", 'ru'),
        ("LyPay — L2Sh Fest Bank", None)
    ]
    LPSB = [
        ("Продавцы Ярмарки", 'ru'),
        ("Fest's Shopkeepers", None)
    ]
    AUC = [
        ("Аукцион Ярмарки", 'ru'),
        ("Fest's Auction", None)
    ]
    LPAA = [
        ("LPAA — LyPay Admin Access", None)
    ]
    SRV = [
        ("LyPay Server", None)
    ]


class PATHS:
    DB = getcwd() + '\\database\\'
    DATA = getcwd() + '\\data\\'

    QR = DB + 'QR\\'
    FIREWALL = DB + 'firewall\\'

    EXE = DATA + 'executor\\'
    IMAGES = DATA + 'images\\'
    LISTS = DATA + 'lists\\'
    EMAIL = DATA + 'email\\'

    DB_BASE = DB + 'base.json'

    FIREWALL_MAIN = FIREWALL + 'MAIN\\'
    FIREWALL_LPAA = FIREWALL + 'LPAA\\'
    FIREWALL_LPSB = FIREWALL + 'LPSB\\'

    STORES_KEYBOARDS = DATA + 'stores keyboards\\'
    STORES_LOGOS = DATA + 'stores logos\\'
    OLD_LOGOS = DATA + 'changed stores logos\\'
    STORES_CHEQUES = DATA + 'cheques\\'

    LAUNCH_SETTINGS = DATA + 'settings.json'

    all = (DB, DATA, EXE, IMAGES, LAUNCH_SETTINGS, QR, STORES_KEYBOARDS, STORES_LOGOS, STORES_CHEQUES,
           OLD_LOGOS, FIREWALL, FIREWALL_MAIN, FIREWALL_LPAA, FIREWALL_LPSB, LISTS, EMAIL)


class MEDIA:
    NOT_IN_LPSB_WHITELIST_FROGS = (
        "CAACAgIAAxkBAAI_xmZPqDQLh1NE36n1xC2-fh_3WECQAAI1AAO_Zp0YnjBB8YeDtUU1BA",
        "CAACAgIAAxkBAAI_xGZPqC3WJ-EkHuNLTdlBfYSHOZhnAAJqDgACtqlwSIhrY4JurVjXNQQ",
        "CAACAgIAAxkBAAI_wmZPqCmdoUVIHdHAEB0LxfJHlHUuAALkDgACkHt4SCXp0KInSRdUNQQ"
    )  # STICKERS

    CREDITS_TEST = "AgACAgIAAxkBAAIw72ZH5ZPCuKxWd2vhWbsIDvyiFdcCAAJn4DEbw1lBSmXxJvUNr3KBAQADAgADdwADNQQ"  # JPG MAIN
    CREDITS = "AgACAgIAAxkBAAIhXGgXnpB6Pz_4cIp1B8FArNA_3luvAAJn4DEbw1lBSgvyIFR1qob5AQADAgADdwADNgQ"

    FROG_HELLO = "CAACAgIAAxkBAAKDe2dDU03iQRW5-nflgjnfRWZGzMC4AAISAAO_Zp0YgifnJzEiFk42BA"  # STICKER

    XILONEN = "CAACAgUAAxkBAAIi3Ggc8RGV9gbZ0aYVH7WENmGeumBsAAKOEQAC-x_4VDGKkVEzKbPuNgQ"  # STICKER

    SERVER_DOWN = "CAACAgIAAxkBAAIjfWgdIDNUyWQXWa08K5pXbZQZPW7sAAKHUAACsBuhSPV809DD3tRoNgQ"  # STICKER

    NOT_IN_LPAA_WHITELIST = "CgACAgQAAxkBAAIJtmZJrQeEu7Y7bL8sG32_cRJlOtmLAAKVBQACVef0UGJrGQjRTdozNQQ"  # GIF LPAA

    BAD_LPSB_REGISTRATION_CODE = {  # RNG VALUE FROM 0 TO 49 INCLUDING BOTH SIDES
        "CAACAgEAAxkBAAIB62d6NKw2rCMaorlVwm7L0AN9tFbTAAJLAQACGdnhAwJjLzPk27XXNgQ": range(0, 11),    # 22%
        "CAACAgEAAxkBAAIB7Wd6NLJEorb1GAg5OR-cIE2HoOp8AALWAQACGdnhA9JJGS-fYNgCNgQ": range(11, 22),   # 22%
        "CAACAgEAAxkBAAIB72d6NLilc2Jzn9M-FH4nYvtlFkC-AAJsAQACGdnhA_RAt-uSZ29FNgQ": range(22, 33),   # 22%
        "CAACAgEAAxkBAAIB8Wd6NL527Ia87ta7gANn6BNLu-AWAAJ5AQACGdnhA56aO8XCKeDBNgQ": range(33, 39),   # 12%
        "CAACAgEAAxkBAAIB82d6NMYHIuLxD1ovJrCp_TXGaDrWAAKPAQACGdnhAyIRoSSu4TLaNgQ": range(39, 50)    # 22%
    }  # STICKERS

    LPSB_MAP = "AgACAgIAAxkBAAKoBGgwhUR84g_cyqlRUDyjRUNBVP5wAALs9zEb_CKJSRUs4lGi2-4lAQADAgADeQADNgQ"  # JPG

    class MANUAL:
        LPSB = "BQACAgIAAxkBAAKMcWghGpBZae73tDA1WBSwJVc8-RFHAAKWaQACIr8ISZJo1PQDG-ZyNgQ"  # PDF
        MAIN = "BQACAgIAAxkBAAKJNWgh-wuSw7fm1xlwYlxvsBBtyzFvAAJHbAACyg0QSfmeI4p1wCSENgQ"  # PDF
        LPSB_TEST = "BQACAgIAAxkBAAIK2Wgc8OaI9IxwhuIit1O5NGwt3wNfAAJtcAACJGjoSMIxnTesm0wwNgQ"
        MAIN_TEST = "BQACAgIAAxkBAAIi2mgc8NOoc7YwwwABYZ4Cyj4Emhe2rQACkW4AAuWE6UgyyVm4Kb5bhDYE"


WARNING_GROUP = -4610376447
HIGH_GROUP = -4573592664
AD_GROUP = -4716284444

VERSION = "v2.3"
NAME = ""
BUILD = 79

CONTACT_TAG = "@IGriB28I"

NEW_LINE_ANCHOR = "[([*br*])]"
OPEN_CURLY_BRACKET_ANCHOR = "[([*ocb*])]"
CLOSE_CURLY_BRACKET_ANCHOR = "[([*ccb*])]"
QUOTATION_ANCHOR = "[([*q*])]"
SPACE_ANCHOR = "[([*s*])]"
