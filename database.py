import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

def create_db():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    # Таблица пользователей (без изменений)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login VARCHAR(1000) NOT NULL DEFAULT '',
            password VARCHAR(1000) NOT NULL DEFAULT ''
        )
    ''')

    # Таблица способностей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS abilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text VARCHAR(1000) NOT NULL DEFAULT ''
        )
    ''')

    # Таблица оружия (добавим её, если её еще нет)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weapons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(1000) NOT NULL DEFAULT '',
            specifications TEXT DEFAULT ''
        )
    ''')

    # Обновленная таблица персонажей (БЕЗ ability_id и weapon_id)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS character (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(1000) NOT NULL DEFAULT '',
            img_path VARCHAR(1000) NOT NULL DEFAULT '',
            img_name VARCHAR(1000) NOT NULL DEFAULT '',
            likes INTEGER DEFAULT 0,
            hp INTEGER DEFAULT 0
        )
    ''')

    # --- ТАБЛИЦЫ СВЯЗЕЙ ---

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS character_abilities (
            character_id INTEGER,
            ability_id INTEGER,
            FOREIGN KEY (character_id) REFERENCES character(id) ON DELETE CASCADE,
            FOREIGN KEY (ability_id) REFERENCES abilities(id) ON DELETE CASCADE,
            PRIMARY KEY (character_id, ability_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS character_weapons (
            character_id INTEGER,
            weapon_id INTEGER,
            FOREIGN KEY (character_id) REFERENCES character(id) ON DELETE CASCADE,
            FOREIGN KEY (weapon_id) REFERENCES weapons(id) ON DELETE CASCADE,
            PRIMARY KEY (character_id, weapon_id)
        )
    ''')

    conn.commit()
    conn.close()

create_db()


def add_abilities():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()


def add_user(login, password):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    hashed_password = generate_password_hash(password)

    cursor.execute("INSERT INTO user (login, password) VALUES (?, ?)", (login, hashed_password))
    print("Created user " + login)
    conn.commit()

def is_user_exists(login):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user WHERE login = ?", (login,))
    user = cursor.fetchone()

    return user != None

def get_users():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user")
    users = cursor.fetchall()
    return users

def auth_user(login, password):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user WHERE login=?", (login,)
                   )
    user = cursor.fetchone()
    if not user:
        return None
    
    if check_password_hash(user[2], password):
        return {
            "user_id": user[0],
            "user_login": user[1]
        }
    else:
        return -1

if __name__ == "__main__":
    create_db()
