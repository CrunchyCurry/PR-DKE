from flask import render_template, url_for, flash, redirect, request, jsonify, session, abort
from functools import wraps

from sqlalchemy.exc import IntegrityError

from . import app, db, bcrypt
from .forms import RegisterForm, LoginForm, StationForm, SectionForm, RailwayForm, SectionAssignment1, \
    SectionAssignment2, WarningForm
from .models import User, Railway, Station, stations_schema, station_schema, Section, Warning, railway_schema, \
    section_schema, warning_schema, railways_schema, sections_schema, warnings_schema, SectionWarning
from flask_login import login_user, current_user, logout_user, login_required


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.check_admin():
            abort(403)
            # return redirect(url_for("login"), code=302)
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
@app.route("/railways")
@login_required
def home():
    railways = Railway.query.all()
    return render_template("home.html", railways=railways)


@app.route("/register", methods=["GET", "POST"])
@login_required
@admin_required
def register():
    # if current_user.is_authenticated:
    #    return redirect(url_for("home"))
    form = RegisterForm()
    if form.validate_on_submit():
        # hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, password=form.password.data, is_admin=form.is_admin.data)
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
        if user:  # and bcrypt.check_password_hash(user.password, form.password.data):
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
@admin_required
@app.route("/section-assignment", methods=["GET", "POST"])
def section_assignment_1():
    form_1 = SectionAssignment1()
    form_1.railway_id.choices = [("0", "---")] + [(s.id, s.name) for s in Railway.query.all()]
    if form_1.validate_on_submit():
        return redirect(url_for("section_assignment_2",
                                railway_id=form_1.railway_id.data))  # redirect to part 2 with chosen railway as param
    return render_template("section_assignment_1.html", title="Abschnitte zu Strecke zuordnen", form=form_1,
                           legend="Abschnitt zu Strecke zuordnen")


@login_required
@admin_required
@app.route("/section-assignment/<int:railway_id>", methods=["GET", "POST"])
def section_assignment_2(railway_id):
    railway = Railway.query.filter_by(id=railway_id).first()
    railway_name = railway.name
    form_2 = SectionAssignment2()
    if railway.get_end_id() is not None:  # if railway already has sections
        form_2.sections.choices = [
            (s.id, f"[{s.id}] {s.start_station.name} - {s.end_station.name} ({s.gauge} mm)") for s in
            Section.query.filter_by(
                railway_id=None,
                starts_at=railway.get_end_id(),
                gauge=railway.get_gauge()
            ).all()
        ]
    else:  # if railway does not have any sections yet
        form_2.sections.choices = [
            (s.id, f"[{s.id}] {s.start_station.name} - {s.end_station.name} ({s.gauge} mm)") for s in
            Section.query.filter_by(railway_id=None).all()
        ]
    if form_2.validate_on_submit():
        print(form_2.sections.data)
        section = Section.query.filter_by(id=form_2.sections.data).first()
        section.railway_id = railway_id
        db.session.commit()
        flash(f"Abschnitt {section.id} wurde zu Strecke {railway_name} zugeordnet!", "success")
        return redirect(url_for("section_assignment_2", railway_id=railway_id))
    return render_template("section_assignment_2.html", title="Abschnitte zu Strecke zuordnen", form=form_2,
                           railway_name=railway_name)


@app.route("/station/new", methods=["GET", "POST"])
@login_required
@admin_required
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
@admin_required
def new_section():
    form = SectionForm()
    form.starts_at.choices = [("0", "---")] + [(s.id, s.name) for s in Station.query.all()]
    form.ends_at.choices = [("0", "---")] + [(s.id, s.name) for s in Station.query.all()]
    # form.railway_id.choices = [("0", "---")] + [(s.id, s.name) for s in Railway.query.all()]
    if form.validate_on_submit():
        section = Section(
            starts_at=form.starts_at.data,
            ends_at=form.ends_at.data,
            length=form.length.data,
            user_fee=form.user_fee.data,
            max_speed=form.max_speed.data,
            gauge=form.gauge.data,
            # railway_id=form.railway_id.data if form.railway_id.data is not 0 else None
        )
        try:
            db.session.add(section)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Es gibt bereits einen Abschnitt mit demselben Start- und End-Bahnhof.", "warning")
            return render_template("create_section.html", title="Neuen Abschnitt erstellen",
                           form=form, lock_stations=False, legend="Neuen Abschnitt erstellen")
        flash("Abschnitt wurde erstellt!", "success")
        return redirect(url_for("sections"))
    return render_template("create_section.html", title="Neuen Abschnitt erstellen",
                           form=form, lock_stations=False, legend="Neuen Abschnitt erstellen")


@app.route("/railway/new", methods=["GET", "POST"])
@login_required
@admin_required
def new_railway():
    form = RailwayForm()
    # form.starts_at.choices = [("0", "---")] + [(s.id, s.name) for s in Station.query.all()]
    # form.ends_at.choices = [("0", "---")] + [(s.id, s.name) for s in Station.query.all()]
    # form.sections.choices = [(s.id, f"Id: {s.id} | {s.start_station.name} - {s.end_station.name})") for s in Section.query.all()]
    if form.validate_on_submit():
        railway = Railway(
            name=form.name.data,
            # starts_at=form.starts_at.data,
            # ends_at=form.ends_at.data,
            # sections=form.sections.data,
        )
        db.session.add(railway)
        db.session.commit()
        flash("Strecke wurde erstellt!", "success")
        return redirect(url_for("home"))
    return render_template("create_railway.html", title="Neue Strecke erstellen",
                           form=form, legend="Neue Strecke erstellen")


@app.route("/warning/new", methods=["GET", "POST"])
@login_required
@admin_required
def new_warning():
    form = WarningForm()
    form.sections.choices = [(s.id, f"[{s.id}] {s.start_station.name} - {s.end_station.name}") for s in
                             Section.query.all()]
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
        flash("Warnung wurde erstellt!", "success")
        return redirect(url_for("warnings"))
    return render_template("create_warning.html", title="Neue Warnung erstellen",
                           form=form, legend="Neue Warnung erstellen")


# <---------------------------- SHOW ONE ---------------------------->

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


@app.route("/warning/<int:warning_id>")
@login_required
def warning(warning_id):
    warning = Warning.query.get_or_404(warning_id)
    return render_template("warning.html", title=warning.title, warning=warning)


@app.route("/user/<int:user_id>")
@login_required
def user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template("user.html", title=user.username, user=user)


# <---------------------------- UPDATE ---------------------------->

@app.route("/user/<int:user_id>/update", methods=["GET", "POST"])
@login_required
@admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    form = RegisterForm()
    # fill in previous data
    if form.validate_on_submit():
        user.username = form.username.data
        user.password = form.password.data
        db.session.commit()
        flash("Benutzer wurde bearbeitet!", "success")
        return redirect(url_for("users", user_id=user.id))
    elif request.method == "GET":
        form.username.data = user.username
        form.password.data = user.password
    return render_template("register.html", title="Benutzer bearbeiten",
                           form=form, legend="Benutzer bearbeiten")


@app.route("/station/<int:station_id>/update", methods=["GET", "POST"])
@login_required
@admin_required
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


@app.route("/warning/<int:warning_id>/update", methods=["GET", "POST"])
@login_required
@admin_required
def update_warning(warning_id):
    warning = Warning.query.get_or_404(warning_id)
    form = WarningForm()
    form.sections.choices = [(s.id, f"[{s.id}] {s.start_station.name} - {s.end_station.name}") for s in
                             Section.query.all()]
    # fill in previous data
    if form.validate_on_submit():
        warning.title = form.title.data
        warning.description = form.description.data
        #warning.sections = form.sections TODO ??? for now only updating title and desc work
        db.session.commit()
        flash("Warnung wurde bearbeitet!", "success")
        return redirect(url_for("warning", warning_id=warning.id))
    elif request.method == "GET":
        # form.sections.data = warning.sections
        print(SectionWarning.query.filter_by(warning_id=warning_id).first().warning_id)
        # no need to check if sections of warnings is empty, because a warning always has one section
        previous_sections = []
        for section in SectionWarning.query.filter_by(warning_id=warning_id).all():
            previous_sections.append(section.id)
        form.sections.process_data(previous_sections)  # select previous sections as default
        form.title.data = warning.title
        form.description.data = warning.description
    return render_template("create_warning.html", title="Warnung bearbeiten",
                           form=form, legend="Warnung bearbeiten")


@app.route("/section/<int:section_id>/update", methods=["GET", "POST"])
@login_required
@admin_required
def update_section(section_id):
    section = Section.query.get_or_404(section_id)
    form = SectionForm()
    form.starts_at.choices = [("0", "---")] + [(s.id, s.name) for s in Station.query.all()]
    form.ends_at.choices = [("0", "---")] + [(s.id, s.name) for s in Station.query.all()]
    lock_stations = False
    # fill in previous data
    if form.validate_on_submit():
        section.starts_at = form.starts_at.data
        section.ends_at = form.ends_at.data
        section.length = form.length.data
        section.user_fee = form.user_fee.data
        section.max_speed = form.max_speed.data
        section.gauge = form.gauge.data
        db.session.commit()
        flash("Abschnitt wurde bearbeitet!", "success")
        return redirect(url_for("section", section_id=section.id))
    elif request.method == "GET":
        lock_stations = True if (section.railway_id is not None) else False
        # print(section.railway_id)
        # print(lock_stations)
        form.starts_at.data = section.starts_at
        form.ends_at.data = section.ends_at
        form.length.data = section.length
        form.user_fee.data = section.user_fee
        form.max_speed.data = section.max_speed
        form.gauge.data = section.gauge

    return render_template("create_section.html", title="Abschnitt bearbeiten",
                           form=form, lock_stations=lock_stations, legend="Abschnitt bearbeiten")
    # lock stations if sections already belongs to a railway


@app.route("/railway/<int:railway_id>/update", methods=["GET", "POST"])
@login_required
@admin_required
def update_railway(railway_id):
    railway = Railway.query.get_or_404(railway_id)
    form = RailwayForm()
    # fill in previous data
    if form.validate_on_submit():
        railway.name = form.name.data
        db.session.commit()
        flash("Strecke wurde bearbeitet!", "success")
        return redirect(url_for("railway", railway_id=railway.id))
    elif request.method == "GET":
        form.name.data = railway.name

    return render_template("create_railway.html", title="Strecke bearbeiten",
                           form=form, legend="Strecke bearbeiten")


# <---------------------------- DELETE ---------------------------->

@app.route("/station/<int:station_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_station(station_id):
    station = Station.query.get_or_404(station_id)
    try:
        db.session.delete(station)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("Bahnhof kann nicht gelöscht werden, wenn dieser noch in Verwendung ist.", "warning")
        return redirect(url_for("station", station_id=station.id))
    flash("Bahnhof wurde gelöscht!", "success")
    return redirect(url_for("stations"))


@app.route("/warning/<int:warning_id>/delete", methods=["POST"])
@login_required
@admin_required
#TODO on delete cascade for sections affecting warnings
def delete_warning(warning_id):
    warning = Warning.query.get_or_404(warning_id)
    db.session.delete(warning)
    db.session.commit()
    flash("Warnung wurde gelöscht!", "success")
    return redirect(url_for("warnings"))


@app.route("/section/<int:section_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_section(section_id):
    section = Section.query.get_or_404(section_id)
    #print(section.railway_id)
    if section.railway_id is not None:
        flash("Abschnitt kann nicht gelöscht werden, solange dieser Bestandteil einer Strecke ist.", "warning")
        return redirect(url_for("section", section_id=section.id))
    warnings = section.warnings
    db.session.delete(section)
    for warning in warnings:
        print(len(warning.sections))
        if len(warning.sections) == 0:
            db.session.delete(warning)
            db.session.commit()
    db.session.commit()
    flash("Abschnitt wurde gelöscht!", "success")
    return redirect(url_for("sections"))


@app.route("/railway/<int:railway_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_railway(railway_id):
    railway = Railway.query.get_or_404(railway_id)
    db.session.delete(railway)
    db.session.commit()
    flash("Strecke wurde gelöscht!", "success")
    return redirect(url_for("home"))


@app.route("/user/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("Benutzer wurde gelöscht!", "success")
    return redirect(url_for("users"))



# <---------------------------- APIs ---------------------------->

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
@admin_required
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
