import datetime

import flask_login
from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user
from flask_wtf import FlaskForm
from sqlalchemy import CheckConstraint, delete
from sqlalchemy.orm import backref, Session
from wtforms import StringField, PasswordField, SubmitField, IntegerField, DateField
from wtforms.validators import InputRequired, Length, ValidationError, EqualTo
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ticket.db'
app.config['SECRET_KEY'] = '123456'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

session = Session()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Models
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, )
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False)


class Action(db.Model):
    __tablename__ = 'action'
    action_id = db.Column(db.Integer, primary_key=True)
    action_name = db.Column(db.String(20), nullable=False)
    action_start = db.Column(db.DATE, nullable=False)
    action_end = db.Column(db.DATE, nullable=False)
    action_discount = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action_user = db.relationship('User', backref=backref('User', uselist=False))


class Train(db.Model):
    __tablename__ = 'train'
    id = db.Column(db.Integer, primary_key=True)


class Route(db.Model):
    __tablename__ = 'route'
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.String, nullable=False)
    end = db.Column(db.String, nullable=False)


class Execution(db.Model):
    __tablename__ = 'execution'
    id = db.Column(db.Integer, primary_key=True)
    depature = db.Column(db.Time, nullable=False)
    date = db.Column(db.DATE, nullable=False)
    trainID = db.Column(db.Integer, db.ForeignKey('train.id'))
    routeID = db.Column(db.Integer, db.ForeignKey('route.id'))
    execution_train = db.relationship('Train', backref=(backref('Train', uselist=False)))
    execution_route = db.relationship('Route', backref=(backref('Route', uselist=False)))


class Ticket(db.Model):
    __tablename__ = 'ticket'
    ticket_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    execution_id = db.Column(db.Integer, db.ForeignKey('execution.id'))
    ticket_user = db.relationship('User', backref=(backref('User-Ticket', uselist=False)))
    ticket_ex = db.relationship('Execution', backref=(backref('Execution', uselist=False)))

# forms
class loginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)],
                           render_kw={"placeholder": "Benutzername"})
    password = PasswordField(validators=[InputRequired(), Length(min=6, max=20)], render_kw={"placeholder": "Passwort"})
    submit = SubmitField("Login")


class registerForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)],
                           render_kw={"placeholder": "Benutzername"})
    password = PasswordField(validators=[InputRequired(), Length(min=6, max=20)], render_kw={"placeholder": "Passwort"})
    repeat_password = PasswordField(validators=[InputRequired(), Length(min=6, max=20), EqualTo("password")],
                                    render_kw={"placeholder": "Passwort wiederholen"})
    submit = SubmitField("Registrieren")

    def validate_user(self, username):
        existing_user = User.query.filter_by(username=username.data).first()

        if existing_user:
            raise ValidationError("Benutzername existiert bereits")


class actionForm(FlaskForm):
    action_id = IntegerField(validators=[InputRequired()], render_kw={"placeholder": "AktionID"})
    action_name = StringField(validators=[InputRequired(), Length(min=1, max=10)], render_kw={"placeholder": "Name"})
    action_start = DateField(validators=[InputRequired()], render_kw={"placeholder": "Beginn"})
    action_end = DateField(validators=[InputRequired()], render_kw={"placeholder": "Ende"})
    action_discount = IntegerField(validators=[InputRequired()],
                                   render_kw={"placeholder": "Rabatt in %"})
    submit = SubmitField("Hinzufügen")

    def validate_date(self):
        if self.action_start > self.action_end:
            raise ValidationError("Das Enddatum darf nicht vor dem Startdatum liegen")


class change_price_campaign_form(FlaskForm):
    action_id = IntegerField(render_kw={"placeholder": "AktionID"})
    action_name = StringField( render_kw={"placeholder": "Name"})
    action_start = DateField(validators=[InputRequired()], render_kw={"placeholder": "Beginn"})
    action_end = DateField(validators=[InputRequired()], render_kw={"placeholder": "Ende"})
    action_discount = IntegerField(validators=[InputRequired()],
                                   render_kw={"placeholder": "Rabatt in %"})
    submit = SubmitField("ändern")







# routes
@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    all_campaigns = Action.query.all()

    return render_template('home.html', cur_user=current_username(), campaigns=all_campaigns)


@app.route('/add_action', methods=['GET', 'POST'])
@login_required
def action_page():
    form = actionForm()
    if form.validate_on_submit():
        new_action = Action(action_id=form.action_id.data, action_name=form.action_name.data,
                            action_start=form.action_start.data, action_end=form.action_end.data,
                            action_discount=form.action_discount.data, user_id=flask_login.current_user.id)
        db.session.add(new_action)
        db.session.commit()

        return redirect(url_for('home'))
    else:
        flash("Hinzufügen war nicht erfolgreich")
    return render_template('add_price_campaign.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = registerForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    else:
        flash("Registrierung war nicht erfolgreich")
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = loginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('home'))

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    object = Action.query.get(id)
    delete(object)
    return redirect(url_for('home'))


@app.route('/edit/<int:id>', methods=['POST'])
def edit(id):
    form = change_price_campaign_form
    return render_template('change_price_campaign.html', id=id, form=form)


def current_username():
    return flask_login.current_user.username

def set_up_new_db():
    return db.drop_all(), db.create_all()


if __name__ == '__main__':
    app.run(debug=True)
