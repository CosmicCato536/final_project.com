import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

def create_db():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login VARCHAR(100) NOT NULL UNIQUE,
        password VARCHAR(100) NOT NULL,
        voted_for INTEGER DEFAULT 0      
    )''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS abilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text VARCHAR(1000) NOT NULL DEFAULT ''
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weapons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(1000) NOT NULL DEFAULT '',
            specifications TEXT DEFAULT ''
        )
    ''')

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

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(100) NOT NULL,
        description VARCHAR(500) NOT NULL
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_achievements (
        user_id INTEGER,
        achievement_id INTEGER,
        PRIMARY KEY (user_id, achievement_id)
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
        cursor.execute("INSERT INTO character (name, img_path, likes, hp) VALUES (?, ?, 0, 125)", (name, path))
    
    conn.commit()
    conn.close()


def fill_achievements():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    
    achievements_list = [
        ("First Blood", "Cast your very first vote for any mercenary on the site."),
        ("Is Doctor In?", "Show respect to the support class and like Medic."),
        ("The Spy Among Us", "Switch your account profile using the top right menu.")
    ]
    
    cursor.execute("DELETE FROM achievements")
    for title, desc in achievements_list:
        cursor.execute("INSERT INTO achievements (title, description) VALUES (?, ?)", (title, desc))
        
    conn.commit()
    conn.close()


def get_characters():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
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
        cursor.execute("UPDATE character SET likes = likes - 1 WHERE id = ?", (char_id,))
        cursor.execute("UPDATE user SET voted_for = 0 WHERE id = ?", (user_id,))
    else:
        if old_vote != 0:
            cursor.execute("UPDATE character SET likes = likes - 1 WHERE id = ?", (old_vote,))
        
        cursor.execute("UPDATE character SET likes = likes + 1 WHERE id = ?", (char_id,))
        cursor.execute("UPDATE user SET voted_for = ? WHERE id = ?", (char_id, user_id))
        
    conn.commit()
    
    cursor.execute("SELECT 1 FROM user_achievements WHERE user_id = ? AND achievement_id = 1", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO user_achievements (user_id, achievement_id) VALUES (?, 1)", (user_id, 1))
        
    if char_id == 7:
        cursor.execute("SELECT 1 FROM user_achievements WHERE user_id = ? AND achievement_id = 2", (user_id,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO user_achievements (user_id, achievement_id) VALUES (?, 2)", (user_id, 2))
            
    conn.commit()
    conn.close()


def add_user(login, password):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    hashed_password = generate_password_hash(password)
    cursor.execute("INSERT INTO user (login, password) VALUES (?, ?)", (login, hashed_password))
    conn.commit()
    conn.close()


def is_user_exists(login):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE login = ?", (login,))
    user = cursor.fetchone()
    conn.close()
    return user is not None


def auth_user(login, password):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, login, password FROM user WHERE login=?", (login,))
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


def get_user_achievements(user_id):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.id, a.title, a.description, 
               CASE WHEN ua.achievement_id IS NOT NULL THEN 1 ELSE 0 END as unlocked
        FROM achievements a
        LEFT JOIN user_achievements ua ON a.id = ua.achievement_id AND ua.user_id = ?
    ''', (user_id,))
    achievements = cursor.fetchall()
    conn.close()
    return achievements


def get_char_details(char_id):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, img_path, likes, hp FROM character WHERE id = ?", (char_id,))
    char_row = cursor.fetchone()
    
    if not char_row:
        conn.close()
        return None

    char_data = {
        "id": char_row[0],
        "name": char_row[1],
        "img_path": char_row[2],
        "likes": char_row[3],
        "hp": char_row[4],
        "abilities": [],
        "weapons": []
    }

    cursor.execute('''
        SELECT a.text FROM abilities a
        JOIN character_abilities ca ON a.id = ca.ability_id
        WHERE ca.character_id = ?
    ''', (char_id,))
    char_data["abilities"] = [row[0] for row in cursor.fetchall()]

    cursor.execute('''
        SELECT w.name, w.specifications FROM weapons w
        JOIN character_weapons cw ON w.id = cw.weapon_id
        WHERE cw.character_id = ?
    ''', (char_id,))
    char_data["weapons"] = [{"name": row[0], "specs": row[1]} for row in cursor.fetchall()]

    conn.close()
    return char_data

if __name__ == "__main__":
    create_db()
    fill_characters()
    fill_achievements()
