from flask import Flask, render_template, request, redirect, url_for, session
import database

app = Flask(__name__)
app.secret_key = "384htoeirgnhufidjkkejhiwfdikwejufdew"

@app.route('/')
def index():
    # Если зашли инкогнито или база пустая — сразу на логин
    if "user_id" not in session or "user_login" not in session:
        return redirect('/login')

    user_vote = database.get_user_vote(session["user_id"])
    chars_list = database.get_characters()
    user_login = session["user_login"] # Убрали дефолтного Солдата, теперь тут строго имя из БД
    
    return render_template('index.html', characters=chars_list, user_vote=user_vote, username=user_login)

@app.route('/info/<int:char_id>')
def info(char_id):
    char = database.get_char_details(char_id) 
    return render_template('info.html', char=char)

@app.route('/like/<int:char_id>')
def like(char_id):
    if "user_id" not in session:
        return redirect('/login')
        
    database.toggle_like(session["user_id"], char_id)
    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_login = request.form.get('login')
        user_password = request.form.get('password')
        errors = []

        if not user_login or not user_password:
            errors.append("Please fill in all fields!")
            return render_template('login.html', errors=errors)

        auth_result = database.auth_user(user_login, user_password)

        if auth_result == -1:
            errors.append("Invalid password!")
            return render_template('login.html', errors=errors)
        elif auth_result is None:
            errors.append("User does not exist!")
            return render_template('login.html', errors=errors)
        else:
            session["user_id"] = auth_result["user_id"]
            session["user_login"] = auth_result["user_login"]
            return redirect('/')

    return render_template('login.html', errors=[])

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html", errors=[])
    elif request.method == "POST":
        login = request.form.get("login")
        pass1 = request.form.get("pass1")
        pass2 = request.form.get("pass2")
        errors = []

        if not login or not pass1 or not pass2:
            errors.append("Please fill in all fields!")
            return render_template("register.html", errors=errors)

        if database.is_user_exists(login):
            errors.append("This user already exists, try another username.")
            
        if pass1 != pass2:
            errors.append("Passwords don't match.")

        if len(pass1) < 4:
            errors.append("The password must contain 4 characters and more.")
        
        if len(errors) == 0:
            database.add_user(login, pass1)
            return redirect('/login')
        else:
            return render_template("register.html", errors=errors)

@app.route('/achievements')
def achievements():
    if "user_id" not in session:
        return redirect('/login')
        
    user_achievements = database.get_user_achievements(session["user_id"])
    user_login = session["user_login"]
    return render_template('achievements.html', achievements=user_achievements, username=user_login)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
        
if __name__ == "__main__":
    app.run(debug=True)
