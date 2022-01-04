from flask import render_template, url_for, flash, redirect, request, jsonify, session
from functools import wraps
from . import app, db, bcrypt
from .forms import RegisterForm, LoginForm, StationForm
from .models import User, Railway, Station, stations_schema, station_schema
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@login_required
def home():
    railways = Railway.query.all()
    return render_template("home.html", railways=railways)


@app.route("/register", methods=["GET", "POST"])
def register():
    # if current_user.is_authenticated:
    #    return redirect(url_for("home"))
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, password=hashed_password, type=True)
        db.session.add(user)
        db.session.commit()
        flash(f"Benutzer {form.username.data} angelegt!", "success")  # second param (success) is category
        return redirect(url_for("register"))
    return render_template("register.html", title="Benutzer anlegen", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)  # log user in
            next_page = request.args.get("next")  # get last page that was accessed to redirect user back to it
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash("Anmeldung fehlgeschlagen. Bitte Benutzername und Passwort prüfen.", "danger")
    return render_template("login.html", title="Anmelden", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/account")
@login_required
def account():
    return render_template("account.html", title="Account")


@app.route("/stations")
@login_required
def stations():
    stations = Station.query.all()
    return render_template("stations.html", title="Bahnhöfe", stations=stations)


@app.route("/station/new", methods=["GET", "POST"])
@login_required
# @login_required
def new_station():
    form = StationForm()
    if form.validate_on_submit():
        station = Station(name=form.name.data, state=form.state.data)
        db.session.add(station)
        db.session.commit()
        flash("Bahnhof wurde erstellt!", "success")
        return redirect(url_for("stations"))
    return render_template("create_station.html", title="Neuen Bahnhof erstellen",
                           form=form, legend="Neuen Bahnhof erstellen")


@app.route("/station/<int:station_id>")
@login_required
def station(station_id):
    station = Station.query.get_or_404(station_id)
    return render_template("station.html", title=station.name, station=station)


@app.route("/station/<int:station_id>/update", methods=["GET", "POST"])
@login_required
# @login_required
def update_station(station_id):
    station = Station.query.get_or_404(station_id)
    form = StationForm()
    # fill in previous data
    if form.validate_on_submit():
        station.name = form.name.data
        station.state = form.state.data
        db.session.commit()
        flash("Bahnhof wurde bearbeitet!", "success")
        return redirect(url_for("station", station_id=station.id))
    elif request.method == "GET":
        form.name.data = station.name
        form.state.data = station.state
    return render_template("create_station.html", title="Bahnhof bearbeiten",
                           form=form, legend="Bahnhof bearbeiten")


#  <!-- check whether user is admin {% if current_user == admin %} --> <!-- endif check -->

@app.route("/station/<int:station_id>/delete", methods=["POST"])
@login_required
# @login_required
def delete_station(station_id):
    station = Station.query.get_or_404(station_id)
    db.session.delete(station)
    db.session.commit()
    flash("Bahnhof wurde gelöscht!", "success")
    return redirect(url_for("stations"))


# API - get all stations
@app.route("/get-stations", methods=["GET"])
def api_stations():
    all_stations = Station.query.all()
    result = stations_schema.dump(all_stations)
    return jsonify(result)


# API - get single station
@app.route("/get-station/<int:id>", methods=["GET"])
def api_station(id):
    station = Station.query.get(id)
    return station_schema.jsonify(station)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('username') is None or session.get('if_logged') is None:
            return redirect(url_for("login"), code=302)
        return f(*args, **kwargs)

    return decorated_function
