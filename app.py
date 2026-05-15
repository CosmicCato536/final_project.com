from flask import Flask, render_template, request, redirect, url_for, session
import database

app = Flask(__name__)
app.secret_key = "384htoeirgnhufidjkkejhiwfdikwejufdew"

@app.route('/')
def index():
    # 1. ЗАЩИТА: Проверяем, вошел ли пользователь на сайт (есть ли его ID в сессии)
    if "user_id" not in session:
        # Если ID нет, сайт сразу переносит пользователя логиниться
        return redirect('/login')

    # 2. Если пользователь успешно авторизован, код идет дальше:
    # Запрашиваем из базы за кого проголосовал этот юзер, чтобы подсветить кнопку зеленым
    user_vote = database.get_user_vote(session["user_id"])
    
    # Запрашиваем список всех 9 наемников из базы данных
    chars_list = database.get_characters()
    
    # 3. Рендерим главную страницу и передаем туда персонажей и голос текущего пользователя
    return render_template('index.html', characters=chars_list, user_vote=user_vote)

@app.route('/like/<int:char_id>')
def like(char_id):
    if "user_id" not in session:
        return redirect('/login')
        
    # 3. Вызываем вашу готовую функцию переключения лайка из библиотеки
    database.toggle_like(session["user_id"], char_id)
    
    return redirect('/')

@app.route('/info/<int:char_id>')
def info(char_id):
    # Берем данные персонажа и его способностей из базы
    char = database.get_char_details(char_id) 
    return render_template('info.html', char=char)

@app.route('/like/<int:char_id>')
def handle_like(char_id):
    if "user_id" not in session:
        return redirect('/login')

    current_liked = session.get('liked_char_id')
    
    # Используем вашу библиотеку для подключения к базе
    conn = database.sqlite3.connect("data.db")
    cursor = conn.cursor()
    
    # Сценарий 1: Отмена лайка на того же самого персонажа
    if current_liked == char_id:
        cursor.execute("UPDATE user SET likes = likes - 1 WHERE id = ?", (char_id,))
        session.pop('liked_char_id', None)
        
    # Сценарий 2: Переключение лайка на другого персонажа
    elif current_liked is not None:
        cursor.execute("UPDATE user SET likes = likes - 1 WHERE id = ?", (current_liked,))
        cursor.execute("UPDATE user SET likes = likes + 1 WHERE id = ?", (char_id,))
        session['liked_char_id'] = char_id
        
    # Сценарий 3: Первый лайк в сессии
    else:
        cursor.execute("UPDATE user SET likes = likes + 1 WHERE id = ?", (char_id,))
        session['liked_char_id'] = char_id
        
    conn.commit()
    conn.close()
    
    return redirect('/')

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        login = request.form["login"]
        pass1 = request.form["pass1"]
        pass2 = request.form["pass2"]
        errors = []
        # проверка существования пользователя
        if database.is_user_exists(login):
            errors.append("This user is already exists, try another username.")
        # проверка на одинаковость паролей
        if pass1 != pass2:
            errors.append("Passwords don`t match.")

        # проверка качества пароля
        if len(pass1) < 4:
            errors.append("The password must contain 4 characters and more.")
        
        if len(errors) == 0:
            database.add_user(login, pass1)
            return render_template("login.html")
        
        else:
            return render_template("register.html", errors=errors)
        
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_val = request.form.get('login')
        password_val = request.form.get('password')

        # 1. Если логин или пароль пустые — выводим английскую ошибку
        if not login_val or not password_val:
            return render_template('login.html', error="Incorrect login or password, try again")

        # 2. Правильный вызов функции через вашу библиотеку database
        auth_user_data = database.auth_user(login_val, password_val)

        # 3. Если библиотека вернула -1 (неверный пароль в базе) — выводим ту же ошибку
        if auth_user_data == -1 or auth_user_data is None:
            return render_template('login.html', error="Incorrect login or password, try again")

        # 4. Если всё успешно, сохраняем сессию и редиректим на главную
        session["user_id"] = auth_user_data["user_id"]
        return redirect('/')

    # 5. Этот return ОБЯЗАТЕЛЬНО должен стоять здесь (для GET-запроса), 
    # чтобы не было ошибки "did not return a valid response"
    return render_template('login.html')


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
        
        
if __name__ == "__main__":
    app.run(debug=True)