from flask import render_template, url_for, flash, redirect, request, jsonify, session
from functools import wraps
from . import app, db, bcrypt
from .forms import RegisterForm, LoginForm, StationForm, SectionForm, RailwayForm, SectionAssignment1, \
    SectionAssignment2, WarningForm
from .models import User, Railway, Station, stations_schema, station_schema, Section, Warning, railway_schema, \
    section_schema, warning_schema, railways_schema, sections_schema, warnings_schema
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
        #hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, password=form.password.data, type=True)
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
        if user: #and bcrypt.check_password_hash(user.password, form.password.data):
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


@app.route("/sections")
@login_required
def sections():
    sections = Section.query.all()
    return render_template("sections.html", title="Abschnitte", sections=sections)


@app.route("/warnings")
@login_required
def warnings():
    warnings = Warning.query.all()
    return render_template("warnings.html", title="Abschnitte", warnings=warnings)


@login_required
@app.route("/section-assignment", methods=["GET", "POST"])
def section_assignment_1():
    form_1 = SectionAssignment1()
    form_1.railway_id.choices = [("0", "---")] + [(s.id, s.name) for s in Railway.query.all()]
    if form_1.validate_on_submit():
        return redirect(url_for("section_assignment_2", railway_id=form_1.railway_id.data))  # redirect to part 2 with chosen railway as param
    return render_template("section_assignment_1.html", title="Abschnitte zu Strecke zuordnen", form=form_1, legend="Abschnitt zu Strecke zuordnen")


@login_required
@app.route("/section-assignment/<int:railway_id>", methods=["GET", "POST"])
def section_assignment_2(railway_id):
    railway_name = Railway.query.filter_by(id=railway_id).first().name
    form_2 = SectionAssignment2()
    form_2.sections.choices = [(s.id, f"Id: {s.id} | {s.start_station.name} - {s.end_station.name}") for s in Section.query.filter_by(railway_id=None).all()]
    if form_2.validate_on_submit():
        print(form_2.sections.data)
        section = Section.query.filter_by(id=form_2.sections.data).first()
        section.railway_id = railway_id
        db.session.commit()
        flash(f"Abschnitt {section.id} wurde zu Strecke {railway_name} zugeordnet!", "success")
        return redirect(url_for("section_assignment_2", railway_id=railway_id))
    return render_template("section_assignment_2.html", title="Abschnitte zu Strecke zuordnen", form=form_2, railway_name=railway_name)


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


@app.route("/section/new", methods=["GET", "POST"])
@login_required
# @login_required
def new_section():
    form = SectionForm()
    form.starts_at.choices = [("0", "---")] + [(s.id, s.name) for s in Station.query.all()]
    form.ends_at.choices = [("0", "---")] + [(s.id, s.name) for s in Station.query.all()]
    #form.railway_id.choices = [("0", "---")] + [(s.id, s.name) for s in Railway.query.all()]
    if form.validate_on_submit():
        section = Section(
            starts_at=form.starts_at.data,
            ends_at=form.ends_at.data,
            length=form.length.data,
            user_fee=form.user_fee.data,
            max_speed=form.max_speed.data,
            gauge=form.gauge.data,
            #railway_id=form.railway_id.data if form.railway_id.data is not 0 else None
        )
        db.session.add(section)
        db.session.commit()
        flash("Abschnitt wurde erstellt!", "success")
        return redirect(url_for("sections"))
    return render_template("create_section.html", title="Neuen Abschnitt erstellen",
                           form=form, legend="Neuen Abschnitt erstellen")


@app.route("/railway/new", methods=["GET", "POST"])
@login_required
# @login_required
def new_railway():
    form = RailwayForm()
    #form.starts_at.choices = [("0", "---")] + [(s.id, s.name) for s in Station.query.all()]
    #form.ends_at.choices = [("0", "---")] + [(s.id, s.name) for s in Station.query.all()]
    #form.sections.choices = [(s.id, f"Id: {s.id} | {s.start_station.name} - {s.end_station.name})") for s in Section.query.all()]
    if form.validate_on_submit():
        railway = Railway(
            name=form.name.data,
            #starts_at=form.starts_at.data,
            #ends_at=form.ends_at.data,
            #sections=form.sections.data,
        )
        db.session.add(railway)
        db.session.commit()
        flash("Strecke wurde erstellt!", "success")
        return redirect(url_for("home"))
    return render_template("create_railway.html", title="Neue Strecke erstellen",
                           form=form, legend="Neue Strecke erstellen")


@app.route("/warning/new", methods=["GET", "POST"])
@login_required
def new_warning():
    form = WarningForm()
    form.sections.choices = [(s.id, f"Id: {s.id} | {s.start_station.name} - {s.end_station.name}") for s in Section.query.all()]
    if form.validate_on_submit():
        warning = Warning(
            title=form.title.data,
            description=form.description.data
        )
        db.session.add(warning)
        for section_id in form.sections.data:
            section = Section.query.get(section_id)
            section.warnings.append(warning)  # do I have to query warning again or is warning obj the same as the inserted one?
        db.session.commit()
        flash("Strecke wurde erstellt!", "success")
        return redirect(url_for("home"))
    return render_template("create_warning.html", title="Neue Warnung erstellen",
                           form=form, legend="Neue Warnung erstellen")


@app.route("/station/<int:station_id>")
@login_required
def station(station_id):
    station = Station.query.get_or_404(station_id)
    return render_template("station.html", title=station.name, station=station)


@app.route("/section/<int:section_id>")
@login_required
def section(section_id):
    section = Section.query.get_or_404(section_id)
    return render_template("section.html", title=f"{section.starts_at} - {section.ends_at}", section=section)


@app.route("/railway/<int:railway_id>")
@login_required
def railway(railway_id):
    railway = Railway.query.get_or_404(railway_id)
    return render_template("railway.html", title=f"{railway.get_start()} - {railway.get_end()}", railway=railway)


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


# API railways
@app.route("/get-railways", methods=["GET"])
def api_railways():
    all_railways = Railway.query.all()
    result = railways_schema.dump(all_railways)
    return jsonify(result)


# API railway
@app.route("/get-railway/<int:id>", methods=["GET"])
def api_railway(id):
    railway = Railway.query.get(id)
    return railway_schema.dump(railway)


# API sections
@app.route("/get-sections", methods=["GET"])
def api_sections():
    all_sections = Section.query.all()
    result = sections_schema.dump(all_sections)
    return jsonify(result)


# API section
@app.route("/get-section/<int:id>", methods=["GET"])
def api_section(id):
    section = Section.query.get(id)
    return section_schema.dump(section)


# API warnings
@app.route("/get-warnings", methods=["GET"])
def api_warnings():
    all_warnings = Warning.query.all()
    result = warnings_schema.dump(all_warnings)
    return jsonify(result)


# API warning
@app.route("/get-warning/<int:id>", methods=["GET"])
def api_warning(id):
    warning = Warning.query.get(id)
    return warning_schema.dump(warning)



@app.route("/users")
@login_required
def users():
    users = User.query.all()
    return render_template("users.html", title="Benutzer", users=users)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('username') is None or session.get('if_logged') is None:
            return redirect(url_for("login"), code=302)
        return f(*args, **kwargs)

    return decorated_function
