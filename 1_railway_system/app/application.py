import flask_bcrypt
from flask import Flask, render_template, url_for, flash, redirect, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import forms  #import RegisterForm, LoginForm, StationForm
from flask_bcrypt import Bcrypt
import os
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate

import sqlite3
import json

app = Flask(__name__)
app.config["SECRET_KEY"] = "3cd7d089a25376da2d10d0b88b429cd1"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///railway.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# "sqlite:1_railway_system/resources/railway.db"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Init ma
ma = Marshmallow(app)


# migrate = Migrate(app, db)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(255), nullable=False)
    type = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"User('{self.username}','{self.type}')"


# TODO: Add starts_at != ends_at constraint<
class Railway(db.Model):
    __tablename__ = "railways"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    # starts_at = db.Column(db.Integer, db.ForeignKey("station.id"), nullable=False)
    # ends_at = db.Column(db.Integer, db.ForeignKey("station.id"), nullable=False)

    # starts_at = db.Column(db.Integer, db.ForeignKey("station.id"))
    # ends_at = db.Column(db.Integer, db.ForeignKey("station.id"))

    starts_at = db.Column(db.Integer, db.ForeignKey("stations.id"))
    ends_at = db.Column(db.Integer, db.ForeignKey("stations.id"))

    def __repr__(self):
        return f"Railway('{self.name}', '{self.starts_at}', '{self.ends_at}')"


class Station(db.Model):
    __tablename__ = "stations"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    state = db.Column(db.String(17), nullable=False)
    start_of = db.relationship('Railway', backref='start_station', lazy='dynamic', foreign_keys='Railway.starts_at')
    end_of = db.relationship('Railway', backref='end_station', lazy='dynamic', foreign_keys='Railway.ends_at')

    def __init__(self, name, state):
        self.name = name
        self.state = state

    def __repr__(self):
        return f"Railway('{self.name}', '{self.state}')"


# Station schema
class StationSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'state')


# Init schema
station_schema = StationSchema()  # use strict = True to avoid console warning
stations_schema = StationSchema(many=True)  # for multiple returns values


# class Section(db.Model):
#     id = db.Column()
#     length = db.Column(db.Numeric())
#     user_fee = db.Column(db.Numeric())
#     max_speed = db.Column(db.Integer)
#     gauge = db.Column(db.Integer)


@app.route("/")
def home():
    railways = Railway.query.all()
    return render_template("home.html", railways=railways)


@app.route("/stations")
def stations():
    stations = Station.query.all()
    return render_template("stations.html", stations=stations)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = flask_bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, password=hashed_password, type=True)
        db.session.add(user)
        db.session.commit()
        flash(f"Benutzer {form.username.data} angelegt!", "success")  # second param (success) is category
        return redirect(url_for("register"))
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


@app.route("/station/new", methods=["GET", "POST"])
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
def station(station_id):
    station = Station.query.get_or_404(station_id)
    return render_template("station.html", title=station.name, station=station)


@app.route("/station/<int:station_id>/update", methods=["GET", "POST"])
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


if __name__ == "__main__":
    app.run(debug=True)
