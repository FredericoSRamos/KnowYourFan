from flask import Flask, render_template, request, session, redirect
from db import init_app, get_db
from helpers import hash_password, check_password

app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY="dev",
    DATABASE="./instance/db.sqlite"
)

app.config.from_pyfile("config.py", silent=True)
init_app(app)

@app.route("/")
def index():
    if "user_id" in session:
        return redirect("/principal")

    return render_template("index.html")

@app.route("/cadastro", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect("/principal")

    if request.method == "GET":
        return render_template("register.html")
    
    name = request.form.get("name")
    cpf = request.form.get("cpf")
    birthdate = request.form.get("birthdate")
    phone = request.form.get("phone")
    email = request.form.get("email")
    address = request.form.get("address")
    about = request.form.get("about")
    events = request.form.get("events")
    purchases = request.form.get("purchases")
    username = request.form.get("username")
    password = request.form.get("password")

    if not name or not cpf or not birthdate or not phone or not phone or not email or not address or not about or not events or not purchases or not username or not password:
        return render_template("register.html", message="Preencha todos os campos obrigatórios")

    try:
        db = get_db()
        db.execute("INSERT INTO users (username, name, cpf, birthdate, phone, email, address, about, events, purchases, password) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (username, name, cpf, birthdate, phone, email, address, about, events, purchases, hash_password(password)))
        db.commit()
    except db.IntegrityError:
        return render_template("register.html", message="Nome de usuário já existe")

    return redirect("/entrar")

@app.route("/entrar", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect("/principal")

    if request.method == "GET":
        return render_template("login.html")
    
    login = request.form.get("login")
    password = request.form.get("password")

    if not login or not password:
        return render_template("login.html", message="Preencha todos os campos")

    db = get_db()
    print(db.execute("SELECT * FROM users").fetchone())
    user = db.execute("SELECT * FROM users WHERE username = ? OR cpf = ?", (login, login)).fetchone()
    if user is None:
        return render_template("login.html", message="Usuário inexistente")

    if not check_password(password, user["password"]):
        return render_template("login.html", message="Senha incorreta")

    session["user_id"] = user["id"]
    return render_template("main.html")

@app.route("/sair")
def logout():
    session.clear()
    return redirect("/")

@app.route("/principal")
def main():
    if "user_id" not in session:
        return redirect("/")
    return render_template("main.html")