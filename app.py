import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

os.makedirs("instance", exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ---------------- USER TABLE ----------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


# ---------------- GAME ACCOUNT TABLE ----------------

class GameAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_name = db.Column(db.String(100))
    game_id = db.Column(db.String(100))
    game_password = db.Column(db.String(100))
    note = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


# ---------------- HOME ----------------

@app.route("/")
def home():

    if "user" in session:
        return redirect(url_for("dashboard"))

    return render_template("index.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET","POST"])
def login():

    if "user" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"].strip()

        # check empty
        if not username or not password:
            flash("⚠ Please enter username and password", "warning")
            return redirect(url_for("login"))

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session["user"] = user.username
            session["user_id"] = user.id

            flash("Login successful 🎉", "success")

            return redirect(url_for("dashboard"))
        else:
            flash("❌ Username or Password incorrect", "error")

            return redirect(url_for("login"))

    return render_template("login.html")


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully", "success")

    return redirect(url_for("login"))


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET","POST"])
def register():

    if "user" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"].strip()

        # check empty
        if not username or not password:
            flash("⚠ Username and password required", "warning")
            return redirect(url_for("register"))

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash("⚠ Username already exists", "warning")
            return redirect(url_for("register"))

        new_user = User(username=username, password=password)

        db.session.add(new_user)
        db.session.commit()

        flash("Register successful 🎉 Please login", "success")

        return redirect(url_for("login"))

    return render_template("register.html")

# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    search = request.args.get("search")

    if search:
        accounts = GameAccount.query.filter(
            GameAccount.user_id == user_id,
            GameAccount.game_name.contains(search)
        ).all()
    else:
        accounts = GameAccount.query.filter_by(user_id=user_id).all()

    # -------- Stats --------

    total_accounts = GameAccount.query.filter_by(user_id=user_id).count()

    total_games = db.session.query(GameAccount.game_name)\
        .filter(GameAccount.user_id == user_id)\
        .distinct().count()

    latest = GameAccount.query.filter_by(user_id=user_id)\
        .order_by(GameAccount.id.desc()).first()

    latest_game = latest.game_name if latest else "None"

    return render_template(
        "dashboard.html",
        accounts=accounts,
        total_accounts=total_accounts,
        total_games=total_games,
        latest_game=latest_game
    )


# ---------------- ADD ACCOUNT ----------------

@app.route("/add", methods=["GET", "POST"])
def add_account():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        new_account = GameAccount(
            game_name=request.form["game_name"],
            game_id=request.form["game_id"],
            game_password=request.form["game_password"],
            note=request.form["note"],
            user_id=session["user_id"]
        )

        db.session.add(new_account)
        db.session.commit()

        flash("Game account added", "success")

        return redirect(url_for("dashboard"))

    return render_template("add_account.html")


# ---------------- DELETE ACCOUNT ----------------

@app.route("/delete/<int:id>")
def delete_account(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    account = GameAccount.query.filter_by(
        id=id,
        user_id=session["user_id"]
    ).first_or_404()

    db.session.delete(account)
    db.session.commit()

    flash("Account deleted", "warning")

    return redirect(url_for("dashboard"))


# ---------------- EDIT ACCOUNT ----------------

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_account(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    account = GameAccount.query.filter_by(
        id=id,
        user_id=session["user_id"]
    ).first_or_404()

    if request.method == "POST":

        account.game_name = request.form["game_name"]
        account.game_id = request.form["game_id"]
        account.game_password = request.form["game_password"]
        account.note = request.form["note"]

        db.session.commit()

        flash("Account updated", "success")

        return redirect(url_for("dashboard"))

    return render_template("edit_account.html", account=account)


# ---------------- RUN APP ----------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)