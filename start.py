# -*- coding: utf-8 -*-

import multiprocessing
import time
import logging
import warnings
from config import CITIES_CONFIG, DEVELOPER_IDS
from database import add_user, init_db


logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

def bootstrap_and_run(city_config: dict):
    """
    Повна процедура для одного міста:
    1. Налаштування логування та попереджень для дочірнього процесу.
    2. Перевірка токена.
    3. Ініціалізація БД та додавання розробників.
    4. Запуск бота.
    """
    
    warnings.filterwarnings("ignore", category=UserWarning)
    logging.getLogger('apscheduler').setLevel(logging.WARNING)
    
    from bot import run_bot
    
    city_name = city_config['city_name']

    if "YOUR_" in city_config["telegram_bot_token"]:
        logger.warning(f"Токен для '{city_name}' не встановлено. Пропускається запуск.")
        print(f"Бот {city_name} | Status | - SKIPPED (Token not set)")
        return

    db_path = city_config['db_path']
    try:
        init_db(db_path)
        for dev_id in DEVELOPER_IDS:
            add_user(db_path, dev_id, 'developer')
        print(f"База даних {city_name} | Status | - OK")
    except Exception as e:
        logger.error(f"Не вдалося налаштувати БД для '{city_name}': {e}")
        print(f"База даних {city_name} | Status | - FAILED")
        return

    try:
        run_bot(city_config)
    except Exception as e:
        logger.error(f"Критична помилка при запуску процесу для '{city_name}': {e}")
        print(f"Бот {city_name} | Status | - FAILED")


if __name__ == "__main__":
    processes = []
    print("--- Запуск ботів BULKA Заміни ---")

    for city_key, config in CITIES_CONFIG.items():
        process = multiprocessing.Process(target=bootstrap_and_run, args=(config,))
        processes.append(process)
        process.start()
        time.sleep(3)

    print("\n--- Статус запуску завершено. Боти працюють у фоновому режимі. ---")
    print("Для зупинки натисніть Ctrl+C.")

    try:
        for process in processes:
            process.join()
    except KeyboardInterrupt:
        print("\n--- Отримано сигнал зупинки. Завершення роботи ботів... ---")
        for process in processes:
            process.terminate() 
            process.join()
        print("--- Усі процеси ботів зупинено. ---")