from flask import Flask, render_template, request, session, redirect, jsonify, url_for
from flask_dance.contrib.twitch import twitch
from helpers import hash_password, check_password, is_file_valid, handle_image, handle_ai_connection, parse_response
from db import get_db, init_app

app = Flask(__name__)

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

    db = get_db()

    user_info = db.execute("SELECT username, about, events, purchases FROM users WHERE id = ?", (session["user_id"],)).fetchone()

    username = user_info["username"]
    about = user_info["about"]
    events = user_info["events"]
    purchases = user_info["purchases"]

    prompt = "\
    Você possui a seguinte descrição sobre um usuário:" + about + "\
    Também sabe que ele participou dos seguintes eventos:" + events + "\
    E também sabe que ele fez as seguintes compras:" + purchases + "\
    Sabendo essas informações sobre o usuário, busque conteúdo sobre e-sports relevante para ele e retorne.\
    Caso não haja informação suficiente para aferir nada sobre o usuário, retorne conteúdo sobre e-sports em geral.\
    **Não forneça nenhuma introdução ou explicação. Apenas retorne o conteúdo das notícias**\
    Lembre-se de que cada notícia deve começar com um título apropriado, seguido de dois pontos (':'), sem marcar elementos ou incluir qualquer texto extra, como introduções ou explicações.\
    "

    response, status_code = handle_ai_connection(app.config["GOOGLE_GEMINI_API_KEY"], prompt)
    print(response)
    if status_code != 200:
        return render_template("main.html", username=username, message="Houve um erro ao carregar o conteúdo principal")

    feed = parse_response(response)

    return render_template("main.html", username=username, feed=feed)

@app.route("/verificar")
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

@app.route("/twitch")
def twitch_login():
    if "user_id" not in session:
        return redirect("/login")

    if not twitch.authorized:
        print("Redirect URI:", url_for("twitch.login"))
        return redirect(url_for("twitch.login"))

    return redirect("/principal")

@app.route("/twitch/authorized")
def twitch_authorized():
    if not twitch.authorized:
        print("Redirect URI:", url_for("twitch.authorized"))
        print("Redirect URI:", url_for("twitch_authorized"))
        return render_template("link.html", message="Erro na autenticação")

    response = twitch.get("users")
    user_info = response.json()

    print(user_info)

    return render_template("link.html", success="Autenticado com sucesso")

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