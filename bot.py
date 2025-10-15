# -*- coding: utf-8 -*-

import logging
import os
import re
from datetime import datetime, timedelta

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    ConversationHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
)
from telegram.error import BadRequest

import database as db
import excel
from excel import MONTHS_UA
from config import AVAILABLE_POSITIONS

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


ASK_DATE, ASK_POSITION, ASK_SHOP = range(3)
ADD_MANAGER_ID = range(3, 4)


def get_main_keyboard(role: str) -> ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton("Знайти заміну")]]
    if role == 'developer':
        keyboard.append([KeyboardButton("Надіслати таблицю")])
        keyboard.append([KeyboardButton("Додати керівника"), KeyboardButton("Видалити керівника")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)



def start(update: Update, context: CallbackContext) -> None:
    config = context.bot_data['config']
    db_path = config['db_path']
    user = update.effective_user
    if not user: return

    db.update_user_username(db_path, user.id, user.username or user.first_name)
    user_data = db.get_user(db_path, user.id)

    if user_data:
        role = user_data['role']
        uk_role = "Розробник" if role == 'developer' else "Керівник"
        update.message.reply_text(f"👋 Привіт, {user.first_name}!\n\nВаша роль: **{uk_role}**.\nЧим можу допомогти?", reply_markup=get_main_keyboard(role), parse_mode='Markdown')
    else:
        update.message.reply_text(f"❌ **Доступ заборонено** ❌\n\nНа жаль, ваш ID (`{user.id}`) не знайдено у базі даних.\nЗверніться до адміністратора.", parse_mode='Markdown')

def cancel(update: Update, context: CallbackContext) -> int:
    config = context.bot_data['config']
    db_path = config['db_path']
    user = update.effective_user
    if not user: return ConversationHandler.END

    logger.info(f"Користувач {user.first_name} скасував розмову.")
    context.user_data.clear()
    user_info = db.get_user(db_path, user.id)
    if user_info:
        update.message.reply_text("👌 Добре, дію скасовано. Ви повернулись у головне меню.", reply_markup=get_main_keyboard(user_info['role']))
    return ConversationHandler.END

def find_replacement_start(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    config = context.bot_data['config']
    db_path = config['db_path']

    user_data = db.get_user(db_path, user.id)

    
    if not user_data or user_data['role'] not in ['manager', 'developer']:
        update.message.reply_text("❌ **Доступ заборонено.**\n\nВи більше не маєте прав створювати заявки.", reply_markup=ReplyKeyboardRemove(), parse_mode='Markdown')
        return ConversationHandler.END

    update.message.reply_text("🗓️ **Крок 1/3: Дата**\n\nНа яку дату потрібна заміна?\nВведіть у форматі `ДД.ММ.РРРР`.", parse_mode='Markdown')
    return ASK_DATE

def ask_date_handler(update: Update, context: CallbackContext) -> int:
    try:
        input_date = datetime.strptime(update.message.text, '%d.%m.%Y').date()
        today = datetime.now().date()

        if input_date < today:
            update.message.reply_text("❌ **Помилка: Минула дата**\n\nНе можна створювати заявки на дати, які вже минули. Будь ласка, введіть сьогоднішню або майбутню дату.", parse_mode='Markdown')
            return ASK_DATE

        context.user_data['replacement_date'] = update.message.text
        kb = [[InlineKeyboardButton(pos, callback_data=pos)] for pos in AVAILABLE_POSITIONS]
        update.message.reply_text(f"🧑‍🍳 **Крок 2/3: Посада**\n\nОберіть посаду для заміни:", reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
        return ASK_POSITION
    except ValueError:
        update.message.reply_text("❗️ **Помилка формату**\n\nБудь ласка, введіть дату саме у форматі `ДД.ММ.РРРР` (наприклад, `25.12.2023`).", parse_mode='Markdown')
        return ASK_DATE

def ask_position_handler(update: Update, context: CallbackContext) -> int:
    config = context.bot_data['config']
    shop_config = config['shop_config']
    query = update.callback_query
    query.answer()
    context.user_data['replacement_position'] = query.data
    kb = [[InlineKeyboardButton(name, callback_data=name)] for name in shop_config.keys()]
    query.edit_message_text(f"🏢 Крок 3/3: Магазин\n\nВи обрали посаду: **{query.data}**.\nТепер оберіть магазин:", reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
    return ASK_SHOP

def ask_shop_handler(update: Update, context: CallbackContext) -> int:
    config = context.bot_data['config']
    db_path = config['db_path']
    shop_config = config['shop_config']
    query = update.callback_query
    user = update.effective_user

    
    user_data = db.get_user(db_path, user.id)
    if not user_data or user_data['role'] not in ['manager', 'developer']:
        query.answer("Доступ заборонено.", show_alert=True)
        query.edit_message_text("❌ **Доступ заборонено.**\n\nВи більше не маєте прав створювати заявки.", parse_mode='Markdown')
        return ConversationHandler.END

    query.answer()
    context.user_data['replacement_shop'] = query.data
    shop_name = context.user_data['replacement_shop']

    repl_id = db.add_replacement(db_path, user.id, user.username or user.first_name, context.user_data['replacement_date'], context.user_data['replacement_position'], shop_name)

    cfg = shop_config[shop_name]
    msg_text = (
        f"🔔 **ПОТРІБНА ЗАМІНА** 🔔\n\n"
        f"📋 Деталі:\n"
        f"🔹 Дата: {context.user_data['replacement_date']}\n"
        f"🔹 Посада: {context.user_data['replacement_position']}\n"
        f"🔹 Магазин: {shop_name}\n\n"
        f"💡 Натисніть кнопку нижче, щоб взяти цю заміну."
    )
    kb = [[InlineKeyboardButton("✅ Взяти заміну", callback_data=f"take_{repl_id}")]]

    try:
        msg = context.bot.send_message(
            chat_id=cfg['chat_id'],
            text=msg_text,
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode='Markdown',
            message_thread_id=cfg.get('thread_id')  # Відправка в конкретну гілку
        )
        db.update_replacement_message_id(db_path, repl_id, msg.message_id, msg.chat_id)
        query.edit_message_text("✅ **Заявку створено!**\n\nВаш запит на заміну було успішно створено та надіслано у відповідну групу.", parse_mode='Markdown')
    except BadRequest as e:
        logger.error(f"Помилка відправки в чат {cfg['chat_id']} для магазину '{shop_name}': {e.message}")
        error_text = "❌ **Невідома помилка**\n\nСталася помилка при відправці. Зверніться до розробника."
        if 'chat not found' in str(e).lower():
            error_text = (
                f"❌ **Помилка: Чат не знайдено!**\n\n"
                f"Не вдалося надіслати повідомлення для магазину **'{shop_name}'**.\n\n"
                f"**Можливі причини:**\n"
                f"1. Бот не був доданий до групи з `chat_id`: `{cfg['chat_id']}`.\n"
                f"2. Вказаний `chat_id` є неправильним.\n\n"
                f"**Що робити:**\n"
                f"1. Додайте бота до відповідної групи.\n"
                f"2. Перевірте `chat_id` в файлі `config.py`."
            )
        query.edit_message_text(error_text, parse_mode='Markdown')


    user_info = db.get_user(db_path, user.id)
    if user_info:
        context.bot.send_message(user.id, "Ви повернулись в головне меню.", reply_markup=get_main_keyboard(user_info['role']))

    context.user_data.clear()
    return ConversationHandler.END

def take_replacement_handler(update: Update, context: CallbackContext) -> None:
    config = context.bot_data['config']
    db_path = config['db_path']
    reports_dir = config['reports_dir']
    query = update.callback_query
    user = update.effective_user

    
    db.update_user_username(db_path, user.id, user.username or user.full_name)

    repl_id = int(query.data.split('_')[1])
    repl_data = db.get_replacement(db_path, repl_id)

    if repl_data and repl_data['status'] == 'pending':
        
        db.take_replacement(db_path, repl_id, user.id, user.full_name, user.username)

        
        mention = f"@{user.username.replace('_', '\\_')}" if user.username else f"[{user.full_name}](tg://user?id={user.id})"

        orig_msg_text = query.message.text
        details_part = orig_msg_text.split("📋 Деталі:")[1].split("💡 Натисніть")[0].strip()

        new_text = (
            f"✅ **ЗАМІНУ ЗНАЙДЕНО** ✅\n\n"
            f"📋 Деталі:\n"
            f"{details_part}\n\n"
            f"👤 Працівник: {mention}\n\n"
            f"❤️‍🔥 Дякую за оперативність! Пам'ятаймо - коли свої підставляють плече — усім легше! ❤️‍🔥"
        )
        query.edit_message_text(new_text, parse_mode='Markdown')
        query.answer("Дякуємо! Ви взяли цю заміну. ✨")

       
        full_details = db.get_full_replacement_details(db_path, repl_id)
        if full_details:
            
            full_details['replacement_worker_full_name'] = user.full_name
            full_details['replacement_worker_username'] = user.username
            full_details['replacement_worker_id'] = user.id
            excel.record_replacement_to_excel(reports_dir, full_details)
    else:
        query.answer("⚠️ Цю заміну вже взяли або скасували.", show_alert=True)

def send_report_handler(update: Update, context: CallbackContext) -> None:
    config = context.bot_data['config']
    reports_dir = config['reports_dir']
    filepath = excel.get_report_filename(reports_dir)
    if os.path.exists(filepath):
        with open(filepath, 'rb') as doc:
            update.message.reply_document(
                document=doc,
                filename=os.path.basename(filepath),
                caption=f"📊 **Звіт по замінах**\n\nОсь актуальний звіт у форматі `.xlsx`.",
                parse_mode='Markdown'
            )
    else:
        update.message.reply_text("🤷‍♂️ Файл звіту ще не було створено для поточного періоду.")

def add_manager_start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("➕ **Додавання керівника**\n\nВведіть Telegram User ID нового керівника.\nДля скасування введіть /cancel.", parse_mode='Markdown')
    return ADD_MANAGER_ID

def ask_manager_id(update: Update, context: CallbackContext) -> int:
    config = context.bot_data['config']
    db_path = config['db_path']
    try:
        user_id = int(update.message.text)
        db.add_user(db_path, user_id, 'manager')
        update.message.reply_text(
            f"✅ **Керівника успішно додано!**\n\n"
            f"🆔 **ID:** `{user_id}`\n"
            f"👨‍💼 Користувач тепер має доступ до функцій керівника.",
            reply_markup=get_main_keyboard('developer'),
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    except ValueError:
        update.message.reply_text("❗️ **Помилка ID**\n\nUser ID має складатися лише з цифр. Спробуйте ще раз.", parse_mode='Markdown')
        return ADD_MANAGER_ID

def remove_manager_menu(update: Update, context: CallbackContext) -> None:
    config = context.bot_data['config']
    db_path = config['db_path']
    managers = db.get_user_by_role(db_path, 'manager')
    if not managers:
        update.message.reply_text("🤷‍♂️ **Список порожній**\n\nНаразі немає жодного керівника для видалення.", parse_mode='Markdown')
        return

    keyboard = []
    for m in managers:
        
        display_name = m['username'] if m['username'] and m['username'] != str(m['user_id']) else f"ID: {m['user_id']}"
        button_text = f"❌ {display_name}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"delete_manager_{m['user_id']}")])

    update.message.reply_text("➖ **Видалення керівника**\n\nОберіть зі списку, кого потрібно видалити:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

def confirm_delete_manager(update: Update, context: CallbackContext) -> None:
    config = context.bot_data['config']
    db_path = config['db_path']
    query = update.callback_query
    query.answer()
    user_id_to_delete = int(query.data.split('_')[2])
    db.delete_user(db_path, user_id_to_delete)
    query.edit_message_text(f"✅ **Користувача видалено**\n\nКерівник з ID `{user_id_to_delete}` більше не має доступу.", parse_mode='Markdown')
    managers = db.get_user_by_role(db_path, 'manager')
    if not managers:
        query.message.reply_text("✅ Всі керівники були видалені.")
        return
    keyboard = [[InlineKeyboardButton(f"❌ {m['username']} (ID: {m['user_id']})", callback_data=f"delete_manager_{m['user_id']}")] for m in managers]
    query.message.reply_text("Оберіть наступного для видалення або поверніться в головне меню.", reply_markup=InlineKeyboardMarkup(keyboard))

def scheduled_report_task(context: CallbackContext) -> None:
    config = context.bot_data['config']
    db_path = config['db_path']
    reports_dir = config['reports_dir']
    now = datetime.now()
    developers = db.get_user_by_role(db_path, 'developer')
    if not developers:
        logger.warning(f"Планувальник ({reports_dir}): не знайдено розробників для відправки звіту.")
        return

    def send_and_delete(filepath: str, caption: str):
        if os.path.exists(filepath):
            filename = os.path.basename(filepath)
            logger.info(f"Надсилання звіту '{filename}' всім розробникам ({reports_dir}).")
            for dev in developers:
                try:
                    with open(filepath, 'rb') as doc:
                        context.bot.send_document(dev['user_id'], document=doc, filename=filename, caption=caption)
                except Exception as e:
                    logger.error(f"Не вдалося надіслати звіт розробнику {dev['user_id']} ({reports_dir}): {e}")
            os.remove(filepath)
            logger.info(f"Файл {filepath} видалено.")
        else:
            logger.warning(f"Планувальник ({reports_dir}): файл звіту {filepath} не знайдено. Пропускаю.")

    city_name = config.get('city_name', 'Місто')

    
    if now.day == 1:
        prev_month_date = now - timedelta(days=1)
        filepath = excel.get_report_filename(reports_dir, for_date=prev_month_date)
        
        
        month_name = excel.MONTHS_UA[prev_month_date.month]
        
        caption = f"📊 **Щомісячний звіт ({city_name})**\n\nОсь повний звіт по замінах за **{month_name}**."
        send_and_delete(filepath, caption)

def run_bot(config: dict) -> None:
    """Налаштовує та запускає один екземпляр бота з заданою конфігурацією."""
    token = config["telegram_bot_token"]

    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    dp.bot_data['config'] = config

    job_queue = updater.job_queue
    job_queue.run_daily(scheduled_report_task, time=datetime.strptime("09:00", "%H:%M").time())

    add_manager_conv = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^Додати керівника$'), add_manager_start)],
        states={ADD_MANAGER_ID: [MessageHandler(Filters.text & ~Filters.command, ask_manager_id)]},
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    escaped_positions = [re.escape(pos) for pos in AVAILABLE_POSITIONS]
    position_pattern = '^(' + '|'.join(escaped_positions) + ')$'

    find_replacement_conv = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^Знайти заміну$'), find_replacement_start)],
        states={
            ASK_DATE: [MessageHandler(Filters.text & ~Filters.command, ask_date_handler)],
            ASK_POSITION: [CallbackQueryHandler(ask_position_handler, pattern=position_pattern)],
            ASK_SHOP: [CallbackQueryHandler(ask_shop_handler)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dp.add_handler(CommandHandler("start", start, filters=Filters.private))
    dp.add_handler(find_replacement_conv)
    dp.add_handler(add_manager_conv)
    dp.add_handler(CallbackQueryHandler(take_replacement_handler, pattern=r'^take_\d+$'))
    dp.add_handler(MessageHandler(Filters.regex('^Надіслати таблицю$'), send_report_handler))
    dp.add_handler(MessageHandler(Filters.regex('^Видалити керівника$'), remove_manager_menu))
    dp.add_handler(CallbackQueryHandler(confirm_delete_manager, pattern=r'^delete_manager_\d+$'))
    dp.add_handler(CommandHandler("cancel", cancel))

    logger.info(f"Бот для '{config['city_name']}' запускається...")
    try:
        updater.start_polling()
        print(f"Бот {config['city_name']} | Status | - OK")
        updater.idle()
    except Exception as e:
        logger.error(f"Помилка під час виконання `start_polling` для '{config['city_name']}': {e}")
        print(f"Бот {config['city_name']} | Status | - FAILED")