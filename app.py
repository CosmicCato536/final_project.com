from flask import Flask, render_template, request, redirect, url_for, session
import database

app = Flask(__name__)
app.secret_key = "384htoeirgnhufidjkkejhiwfdikwejufdew"

@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    return render_template("index.html", user_login=session["login"])

@app.route('/change_status', methods=['POST'])
def change_status():
    task_id = request.form.get('task-id')

    if task_id:
        database.change_task_status(task_id)
    return redirect(url_for('index'))

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
        
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        login = request.form["login"]
        password = request.form["password"]

        auth_user= database.auth_user(login, password)
        if auth_user == None:
            return render_template("login.html", errors=["Неверный логин или пароль"])
        else:
            print('Successful registration!')
            session["user_id"] = auth_user["user_id"]
            session["login"] = auth_user["user_login"]
            return redirect(url_for('index'))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
        
        
if __name__ == "__main__":
    app.run(debug=True)