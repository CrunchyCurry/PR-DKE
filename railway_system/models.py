from flask_login import UserMixin

from . import db, login_manager, ma


# Station schema
class StationSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'state')


# Init schema
station_schema = StationSchema()  # use strict = True to avoid console warning
stations_schema = StationSchema(many=True)  # for multiple returns values


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(255), nullable=False)
    type = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"User('{self.username}','{self.type}')"


# TODO: Add starts_at != ends_at constraint<
class Railway(db.Model):
    __tablename__ = "railway"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    starts_at = db.Column(db.Integer, db.ForeignKey("station.id"), nullable=False)
    ends_at = db.Column(db.Integer, db.ForeignKey("station.id"), nullable=False)
    sections = db.relationship("Section", backref='on_railway', lazy='dynamic')

    def __repr__(self):
        return f"Railway('{self.name}', '{self.starts_at}', '{self.ends_at}')"


class Station(db.Model):
    __tablename__ = "station"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    state = db.Column(db.String(17), nullable=False)
    # for railways
    start_of_r = db.relationship('Railway', backref='start_station', lazy='dynamic', foreign_keys='Railway.starts_at')
    end_of_r = db.relationship('Railway', backref='end_station', lazy='dynamic', foreign_keys='Railway.ends_at')
    # for sections
    start_of_s = db.relationship('Section', backref='start_station', lazy='dynamic', foreign_keys='Section.starts_at')
    end_of_s = db.relationship('Section', backref='end_station', lazy='dynamic', foreign_keys='Section.ends_at')

    def __init__(self, name, state):
        self.name = name
        self.state = state

    def __repr__(self):
        return f"Railway('{self.name}', '{self.state}')"


class Section(db.Model):
    __tablename__ = "section"
    id = db.Column(db.Integer, primary_key=True)
    starts_at = db.Column(db.Integer, db.ForeignKey("station.id"), nullable=False)
    ends_at = db.Column(db.Integer, db.ForeignKey("station.id"), nullable=False)
    length = db.Column(db.Numeric(), nullable=False)
    user_fee = db.Column(db.Numeric(), nullable=False)
    max_speed = db.Column(db.Integer, nullable=False)
    gauge = db.Column(db.Integer, nullable=False)
    railway_id = db.Column(db.Integer, db.ForeignKey("railway.id"))
    warnings = db.relationship("Warning", backref='on_section', lazy='dynamic')


class Warning(db.Model):
    __tablename__ = "warning"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey("section.id"), nullable=False)

