from flask import Flask, render_template, url_for, flash, redirect
from forms import RegisterForm, LoginForm
import sqlite3
import json

app = Flask(__name__)

app.config["SECRET_KEY"] = "3cd7d089a25376da2d10d0b88b429cd1"


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        flash(f"Benutzer {form.username.data} angelegt!", "success")  # second param (success) is category
        return redirect(url_for("home"))
    return render_template("register.html", title="Benutzer anlegen", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == "admin" and form.password.data == "admin":
            flash("Erfolgreich angemeldet!", "success")
            return redirect(url_for("home"))
        else:
            flash("Anmeldung fehlgeschlagen. Benutzername und/oder Passwort falsch!", "danger")
    return render_template("login.html", title="Anmelden", form=form)


if __name__ == "__main__":
    app.run(debug=True)
