import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

def create_db():
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()
    sql = '''CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            login VARCHAR(1000) NOT NULL DEFAULT '',
            password VARCHAR(1000) NOT NULL DEFAULT '',
            liked
        )
          '''
    cursor.execute(sql)

    sql = '''CREATE TABLE IF NOT EXISTS task (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            text VARCHAR(1000) NOT NULL DEFAULT '',
            is_done INTEGER DEFAULT  0,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES user(id)
        )
          '''
    cursor.execute(sql)


    conn.commit()

def add_user(login, password):
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()
    hashed_password = generate_password_hash(password)

    cursor.execute("INSERT INTO user (login, password) VALUES (?, ?)", (login, hashed_password))
    print("Created user " + login)
    conn.commit()

def is_user_exists(login):
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user WHERE login = ?", (login,))
    user = cursor.fetchone()

    return user != None

def get_users():
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user")
    users = cursor.fetchall()
    return users

def auth_user(login, password):
    conn = sqlite3.connect("todo.db")
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
