# -*- coding: utf-8 -*-
import sqlite3
import os

def init_db(db_path: str):
    """Ініціалізує базу даних, створює таблиці та виконує міграцію, якщо потрібно."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT, -- Може бути NULL спочатку
            role TEXT NOT NULL CHECK(role IN ('developer', 'manager'))
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS replacements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manager_id INTEGER, manager_username TEXT, request_date TEXT,
            position TEXT, shop TEXT, status TEXT DEFAULT 'pending',
            replacement_worker_id INTEGER, 
            replacement_worker_full_name TEXT, 
            replacement_worker_username TEXT,
            message_id INTEGER, chat_id INTEGER,
            FOREIGN KEY (manager_id) REFERENCES users (user_id)
        )
    ''')

    cur.execute("PRAGMA table_info(replacements)")
    columns = [column[1] for column in cur.fetchall()]
    
    if 'replacement_worker_full_name' not in columns:
        print("Виконую міграцію: додаю колонку 'replacement_worker_full_name'...")
        cur.execute("ALTER TABLE replacements ADD COLUMN replacement_worker_full_name TEXT")
    
    if 'replacement_worker_username' not in columns:
        print("Виконую міграцію: додаю колонку 'replacement_worker_username'...")
        cur.execute("ALTER TABLE replacements ADD COLUMN replacement_worker_username TEXT")

    con.commit()
    con.close()

def add_user(db_path: str, user_id: int, role: str):
    """Додає нового користувача (лише за ID) або ігнорує, якщо він вже існує."""
    if role not in ['developer', 'manager']:
        print(f"Помилка: Невірна роль '{role}'.")
        return
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    try:
        cur.execute("INSERT OR IGNORE INTO users (user_id, role) VALUES (?, ?)", (user_id, role))
        con.commit()
    finally:
        con.close()

def update_user_username(db_path: str, user_id: int, username: str):
    """Оновлює username для існуючого користувача."""
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("UPDATE users SET username = ? WHERE user_id = ?", (username, user_id))
    con.commit()
    con.close()

def get_user(db_path: str, user_id: int):
    """Отримує дані користувача за його ID."""
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("SELECT user_id, username, role FROM users WHERE user_id = ?", (user_id,))
    user = cur.fetchone()
    con.close()
    if user:
        return {"user_id": user[0], "username": user[1], "role": user[2]}
    return None

def delete_user(db_path: str, user_id: int):
    """Видаляє користувача з бази даних за його ID."""
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    con.commit()
    con.close()
    print(f"Користувача з ID {user_id} видалено.")

def get_user_by_role(db_path: str, role: str) -> list:
    """Повертає список користувачів з вказаною роллю."""
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("SELECT user_id, username FROM users WHERE role = ?", (role,))
    users = cur.fetchall()
    con.close()
    return [{"user_id": user[0], "username": user[1] or f"ID: {user[0]}"} for user in users]

def add_replacement(db_path: str, manager_id: int, manager_username: str, request_date: str, position: str, shop: str) -> int:
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("INSERT INTO replacements (manager_id, manager_username, request_date, position, shop) VALUES (?, ?, ?, ?, ?)", (manager_id, manager_username, request_date, position, shop))
    con.commit()
    replacement_id = cur.lastrowid
    con.close()
    return replacement_id

def update_replacement_message_id(db_path: str, replacement_id: int, message_id: int, chat_id: int):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("UPDATE replacements SET message_id = ?, chat_id = ? WHERE id = ?", (message_id, chat_id, replacement_id))
    con.commit()
    con.close()

def get_replacement(db_path: str, replacement_id: int):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("SELECT id, status FROM replacements WHERE id = ?", (replacement_id,))
    data = cur.fetchone()
    con.close()
    if data: return {"id": data[0], "status": data[1]}
    return None

def get_full_replacement_details(db_path: str, replacement_id: int) -> dict | None:
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("""
        SELECT id, manager_username, request_date, position, shop, 
               replacement_worker_id, replacement_worker_full_name, replacement_worker_username 
        FROM replacements WHERE id = ?
    """, (replacement_id,))
    data = cur.fetchone()
    con.close()
    if data:
        return {
            "id": data[0], "manager_username": data[1], "request_date": data[2],
            "position": data[3], "shop": data[4], "replacement_worker_id": data[5],
            "replacement_worker_full_name": data[6], "replacement_worker_username": data[7]
        }
    return None

def take_replacement(db_path: str, replacement_id: int, worker_id: int, worker_full_name: str, worker_username: str | None):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("""
        UPDATE replacements 
        SET status = 'taken', 
            replacement_worker_id = ?, 
            replacement_worker_full_name = ?, 
            replacement_worker_username = ? 
        WHERE id = ?
    """, (worker_id, worker_full_name, worker_username, replacement_id))
    con.commit()
    con.close()

if __name__ == '__main__':
    DB_FILE_EXAMPLE = "bulka_example.db"
    init_db(DB_FILE_EXAMPLE)
    print(f"Базу даних '{DB_FILE_EXAMPLE}' створено/перевірено.")