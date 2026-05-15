import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

def create_db():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login VARCHAR(100) NOT NULL UNIQUE,
        password VARCHAR(100) NOT NULL,
        voted_for INTEGER DEFAULT 0      
    )''')

    # Таблица способностей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS abilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text VARCHAR(1000) NOT NULL DEFAULT ''
        )
    ''')

    # Таблица оружия
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weapons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(1000) NOT NULL DEFAULT '',
            specifications TEXT DEFAULT ''
        )
    ''')

    # Таблица персонажей
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

    # Таблицы связей
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

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_likes (
        user_id INTEGER,
        char_id INTEGER,
        PRIMARY KEY (user_id, char_id) 
    )''')

    conn.commit()
    conn.close()


def fill_characters():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    
    chars = [
        ('Scout', 'static/img/scout.png'),
        ('Soldier', 'static/img/solider.png'),
        ('Pyro', 'static/img/pyro.png'),
        ('Demoman', 'static/img/demo.png'),
        ('Heavy', 'static/img/hevy.png'),
        ('Engineer', 'static/img/engineer.png'),
        ('Medic', 'static/img/medic.png'),
        ('Sniper', 'static/img/sniper.png'),
        ('Spy', 'static/img/spy.png')
    ]
    
    cursor.execute("DELETE FROM character")
    for name, path in chars:
        cursor.execute("INSERT INTO character (name, img_path, likes) VALUES (?, ?, 0)", (name, path))
    
    conn.commit()
    conn.close()
    print("Наемники зачислены в базу!")


# ЭТА ФУНКЦИЯ ТЕПЕРЬ ДОСТУПНА ДЛЯ ИМПОРТА В app.py
def get_characters():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    # Вытягиваем: id (0), name (1), img_path (2), likes (3)
    cursor.execute("SELECT id, name, img_path, likes FROM character")
    characters = cursor.fetchall()
    conn.close()
    return characters


def get_user_vote(user_id):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT voted_for FROM user WHERE id = ?", (user_id,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else 0


def toggle_like(user_id, char_id):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT voted_for FROM user WHERE id = ?", (user_id,))
    res = cursor.fetchone()
    old_vote = res[0] if res else 0

    if old_vote == char_id:
        # Отмена текущего лайка
        cursor.execute("UPDATE character SET likes = likes - 1 WHERE id = ?", (char_id,))
        cursor.execute("UPDATE user SET voted_for = 0 WHERE id = ?", (user_id,))
    else:
        # Если ранее был лайкнут другой персонаж, снимаем с него голос
        if old_vote != 0:
            cursor.execute("UPDATE character SET likes = likes - 1 WHERE id = ?", (old_vote,))
        
        # Записываем новый голос
        cursor.execute("UPDATE character SET likes = likes + 1 WHERE id = ?", (char_id,))
        cursor.execute("UPDATE user SET voted_for = ? WHERE id = ?", (char_id, user_id))
        
    conn.commit()
    conn.close()


def add_user(login, password):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    hashed_password = generate_password_hash(password)
    cursor.execute("INSERT INTO user (login, password) VALUES (?, ?)", (login, hashed_password))
    print("Created user " + login)
    conn.commit()
    conn.close()


def is_user_exists(login):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE login = ?", (login,))
    user = cursor.fetchone()
    conn.close()
    return user is not None


def get_users():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user")
    users = cursor.fetchall()
    conn.close()
    return users


def auth_user(login, password):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE login=?", (login,))
    user = cursor.fetchone()
    conn.close()
    
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
    fill_characters()