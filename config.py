
import os


CITIES_CONFIG = {
    "khmelnytskyi": {
        "city_name": "Хмельницький",
        "telegram_bot_token": os.getenv("KHMELNYTSKYI_BOT_TOKEN", "8253028483:AAFALHld0rXY61kldN4JvmefgIQF87VtLOQ"),
        "db_path": "instance/khmelnytskyi/bulka.db",
        "employees_db_path": "instance/khmelnytskyi/employees.db",
        "reports_dir": "instance/khmelnytskyi/reports",
        "available_positions": [
            "Старший продавець",
            "Продавець-консультант (каса)",
            "Продавець відділу гастрономії",
            "Продавець відділу кулінарії",
            "Продавець (сер. зміна)",
            "Продавець-приймальник",
            "Підсобний робітник"
        ],
        "shop_config": {
            "B-19 вул. Героїв Маріуполя, 62": {"chat_id": -1002735339327, "thread_id": 13},
            "B-17 проспект Миру, 69": {"chat_id": -1002735339327, "thread_id": 9},
            "B-4 Деражня": {"chat_id": -1002735339327, "thread_id": 96},
            "B-24 вул. Камянецька, 52/2": {"chat_id": -1002735339327, "thread_id": 19},
            "B-29 вул. Шевченка, 39": {"chat_id": -1002735339327, "thread_id": 23},
            "B-8 вул. Тернопільська, 30/2а": {"chat_id": -1002735339327, "thread_id": 5},
            "B-1 вул. Степана Бандери, 17": {"chat_id": -1002735339327, "thread_id": 3},
            "B-20 проспект Миру, 62а": {"chat_id": -1002735339327, "thread_id": 15},
            "B-12 вул. Олександра Кушнірука 6/1": {"chat_id": -1002735339327, "thread_id": 7},
            "B-18 вул. Тернопільська, 20/1": {"chat_id": -1002735339327, "thread_id": 11},
            "B-23 вул. Залізняка, 8/3": {"chat_id": -1002735339327, "thread_id": 17},
            "B-26 вул. Водопровідна, 75/2": {"chat_id": -1002735339327, "thread_id": 21},
            "BAD CAT вул. Зарічанська, 16": {"chat_id": -1002735339327, "thread_id": 28},
            "B-32 вул. Трудова 40": {"chat_id": -1002735339327, "thread_id": 26},
        }
    },


    "kamianets": {
        "city_name": "Кам'янець-Подільський",
        "telegram_bot_token": os.getenv("KAMIANETS_BOT_TOKEN", "8332963965:AAGb_JQGdWWJ34fvJO0bfAwvYIGRjg8FF3k"),
        "db_path": "instance/kamianets/bulka.db",
        "employees_db_path": "instance/kamianets/employees.db",
        "reports_dir": "instance/kamianets/reports",
        "available_positions": [
            "Старший продавець",
            "Продавець-консультант (каса)",
            "Продавець відділу гастрономії",
            "Продавець відділу кулінарії",
            "Продавець (сер. зміна)",
            "Продавець-приймальник",
            "Підсобний робітник"
        ],
        "shop_config": {
            "B-31 вул. Юрія Руфа, 5": {"chat_id": -1003142282648, "thread_id": 23},
            "B-30 вул. Є. Коновальця 5а(SAKURA)": {"chat_id": -1003142282648, "thread_id": 21},
            "B-25 вул. Ярослава Мудрого, 134": {"chat_id": -1003142282648, "thread_id": 19},
            "B-22 вул. Миру, 4": {"chat_id": -1003142282648, "thread_id": 17},
            "B-21 вул. Любомира Гузара, 5": {"chat_id": -1003142282648, "thread_id": 15},
            "B-16 вул. Степана Бандери, 65": {"chat_id": -1003142282648, "thread_id": 13},
            "B-15 вул. Князів Коріатовичів 25": {"chat_id": -1003142282648, "thread_id": 11},
            "B-9  вул. Героїв ЗСУ, 8": {"chat_id": -1003142282648, "thread_id": 9},
            "B-6  вул. Героїв Небесної Сотні, 4": {"chat_id": -1003142282648, "thread_id": 7},
            "B-5  вул. Шевченка, 4": {"chat_id": -1003142282648, "thread_id": 5},
            "B-2  вул. Панівецька, 5": {"chat_id": -1003142282648, "thread_id": 3},
        }
    },

    "khmelnytskyi_vlasne": {
        "city_name": "Хмельницький (Власне)",
        "telegram_bot_token": os.getenv("KHMELNYTSKYI_VLASNE_BOT_TOKEN", "8265168087:AAGghsfeQMmCzQQQNxtXyU4SBaJcUApH0rM"),
        "db_path": "instance/khmelnytskyi_vlasne/bulka.db",
        "employees_db_path": "instance/khmelnytskyi_vlasne/employees.db",
        "reports_dir": "instance/khmelnytskyi_vlasne/reports",
        "available_positions": [
            "Зав. виробництва",
            "Старший зміни",
            "Пекар",
            "Фаст-фуд",
            "Піцеолог",
            "Кухар",
            "Фасувальник",
            "Підсобний робітник"
        ],
        "shop_config": {
            "B-29 вул. Шевченка, 39": {"chat_id": -1002933548791, "thread_id": 13},
            "B-20 проспект Миру, 62а": {"chat_id": -1002933548791, "thread_id": 11},
            "Виробничий цех ХМ": {"chat_id": -1002933548791, "thread_id": 26},
            "Кондитерський Цех ХМ": {"chat_id": -1002933548791, "thread_id": 24},
            "B-17 проспект Миру, 69": {"chat_id": -1002933548791, "thread_id": 7},
            "B-4 Деражня": {"chat_id": -1002933548791, "thread_id": 4},
        }
    },

    "kamianets_vlasne": {
        "city_name": "Кам'янець-Подільський (Власне)",
        "telegram_bot_token": os.getenv("KAMIANETS_VLASNE_BOT_TOKEN", "8230235189:AAHWYOwoWJMX8hxBvyLcDAQIqsMe5BMrXh8"),
        "db_path": "instance/kamianets_vlasne/bulka.db",
        "employees_db_path": "instance/kamianets_vlasne/employees.db",
        "reports_dir": "instance/kamianets_vlasne/reports",
        "available_positions": [
            "Зав. виробництва",
            "Старший зміни",
            "Пекар",
            "Фаст-фуд",
            "Піцеолог",
            "Кухар",
            "Фасувальник",
            "Підсобний робітник"
        ],
        "shop_config": {
            "B-30 вул. Є. Коновальця 5а(SAKURA)": {"chat_id": -1003121338903, "thread_id": 13},
            "B-15 вул. Князів Коріатовичів 25": {"chat_id": -1003121338903, "thread_id": 11},
            "B-16 вул. Степана Бандери, 65": {"chat_id": -1003121338903, "thread_id": 9},
            "B-6  вул. Героїв Небесної Сотні, 4": {"chat_id": -1003121338903, "thread_id": 7},
            "B-5  вул. Шевченка, 4": {"chat_id": -1003121338903, "thread_id": 5},
            "B-2  вул. Панівецька, 5": {"chat_id": -1003121338903, "thread_id": 3},
        }
    }
}

DEVELOPER_IDS = [
    738460434,
    1001226587,
    699459866,
    709321162, 
]