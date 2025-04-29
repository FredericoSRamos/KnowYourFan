from flask import Flask, render_template, request, session, redirect, jsonify
from helpers import hash_password, check_password, is_file_valid, handle_image, handle_ai_connection
from db import get_db, init_app

app = Flask(__name__)

app.config.from_pyfile("config.py")
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

    if not name or not cpf or not birthdate or not phone or not phone or not email or not address or not about or not username or not password:
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

    user = db.execute("SELECT * FROM users WHERE username = ? OR cpf = ? OR email = ?", (login, login, login)).fetchone()
    if user is None:
        return render_template("login.html", message="Usuário inexistente")

    if not check_password(password, user["password"]):
        return render_template("login.html", message="Senha incorreta")

    session["user_id"] = user["id"]
    return redirect("/principal")

@app.route("/sair")
def logout():
    session.clear()
    return redirect("/")

@app.route("/principal")
def main():
    if "user_id" not in session:
        return redirect("/login")

    return render_template("main.html")

@app.route("/verificar", methods=["GET"])
def verify():
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()

    user_info = db.execute("SELECT is_verified FROM users WHERE id = ?", (session["user_id"],)).fetchone()

    if user_info["is_verified"] == 1:
        is_verified = True
    else:
        is_verified = False

    return render_template("verify.html", is_verified=is_verified)

@app.route("/vincular", methods=["GET", "POST"])
def link():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "GET":
        return render_template("link.html")

@app.route("/bot-response", methods=["POST"])
def get_bot_response():
    if "user_id" not in session:
        return jsonify({ "error": "Usuário não registrado" }), 400

    data = request.get_json()
    prompt = data.get("message")

    if not prompt:
        return jsonify({ "error": "Nenhuma mensagem fornecida" }), 400
    
    response, status_code = handle_ai_connection(app.config["GOOGLE_GEMINI_API_KEY"], prompt)

    return jsonify({ "message": response }), status_code

@app.route("/upload-documents", methods=["POST"])
def upload_documents():
    if "user_id" not in session:
        return redirect("/login")

    if "identity-card" not in request.files:
        return render_template("verify.html", message="Nenhum arquivo selecionado")

    file = request.files["identity-card"]

    if not file.filename or not is_file_valid(file.filename):
        return render_template("verify.html", message="Arquivo inválido")

    image = handle_image(file)

    prompt = f"{image}\nO que voce ve nessa imagem?"

    db = get_db()
    user_information = db.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()

    if user_information is None:
        return render_template("verify.html", message="Usuário inexistente")

    query = "Com base nas seguintes informações do usuário, verifique se a imagem corresponde a um documento válido. Sua resposta deve ser 1 caso o documento seja válido e 0 caso não seja válido, e nada além destes dois números:"
    prompt = query + "\n\n" + str(user_information) + "\n\n" + image

    response, status_code = handle_ai_connection(app.config["GOOGLE_GEMINI_API_KEY"], prompt)

    if status_code == 200:
        if response.strip() == "1":
            db.execute("UPDATE users SET is_verified = 1 WHERE id = ?", (session["user_id"],))
            db.commit()

            return redirect("/principal")
        else:
            return render_template("verify.html", message="Verificação invalidada, verifique seus documentos e tente novamente")

    return render_template("verify.html", message=response)