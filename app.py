from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    
class GameAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_name = db.Column(db.String(100), nullable=False)
    game_id = db.Column(db.String(100), nullable=False)
    game_password = db.Column(db.String(100), nullable=False)
    note = db.Column(db.String(200))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            return redirect(url_for("dashboard"))
        else:
            return "Invalid username or password"

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        new_user = User(username=username, password=password)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/dashboard")
def dashboard():

    search = request.args.get("search")

    if search:
        accounts = GameAccount.query.filter(
            GameAccount.game_name.contains(search)
        ).all()
    else:
        accounts = GameAccount.query.all()

    return render_template("dashboard.html", accounts=accounts)
@app.route("/add", methods=["GET", "POST"])
def add_account():

    if request.method == "POST":
        game_name = request.form["game_name"]
        game_id = request.form["game_id"]
        game_password = request.form["game_password"]
        note = request.form["note"]

        new_account = GameAccount(
            game_name=game_name,
            game_id=game_id,
            game_password=game_password,
            note=note
        )

        db.session.add(new_account)
        db.session.commit()

        return redirect(url_for("dashboard"))

    return render_template("add_account.html")

@app.route("/delete/<int:id>")
def delete_account(id):

    account = GameAccount.query.get(id)

    db.session.delete(account)
    db.session.commit()

    return redirect(url_for("dashboard"))

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_account(id):
    account = GameAccount.query.get_or_404(id)

    if request.method == "POST":
        account.game_name = request.form["game_name"]
        account.game_id = request.form["game_id"]
        account.game_password = request.form["game_password"]
        account.note = request.form["note"]

        db.session.commit()
        return redirect(url_for("dashboard"))

    return render_template("edit_account.html", account=account)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)