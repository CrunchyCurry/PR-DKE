from flask_login import UserMixin
from marshmallow import fields
from sqlalchemy import UniqueConstraint, CheckConstraint
from sqlalchemy.orm import backref

from . import db, login_manager, ma


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)

    #TODO add is admin method
    def check_admin(self):
        return self.is_admin

    def __repr__(self):
        return f"User('{self.username}','{self.is_admin}')"


class Station(db.Model):
    __tablename__ = "station"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    state = db.Column(db.String(17), nullable=False)
    # for railways
    #start_of_r = db.relationship('Railway', backref='start_station', lazy='dynamic', foreign_keys='Railway.starts_at')
    #end_of_r = db.relationship('Railway', backref='end_station', lazy='dynamic', foreign_keys='Railway.ends_at')
    # for sections
    start_of_s = db.relationship('Section', backref='start_station', lazy='dynamic', foreign_keys='Section.starts_at')
    end_of_s = db.relationship('Section', backref='end_station', lazy='dynamic', foreign_keys='Section.ends_at')


    def __init__(self, name, state):
        self.name = name
        self.state = state

    def __repr__(self):
        return f"Railway('{self.name}', '{self.state}')"


# TODO: Add starts_at != ends_at constraint<
class Railway(db.Model):
    __tablename__ = "railway"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    #starts_at = #db.Column(db.Integer, db.ForeignKey("station.id"))#, nullable=False)
    #ends_at = #db.Column(db.Integer, db.ForeignKey("station.id"))#, nullable=False)
    sections = db.relationship("Section", backref='on_railway', lazy='select')

    def get_start(self):
        if len(self.sections) != 0:
            return Station.query.get(self.sections[0].starts_at).name
        return None

    def get_end(self):
        if len(self.sections) != 0:
            return Station.query.get(self.sections[-1].ends_at).name
        return None

    def get_end_id(self):
        if len(self.sections) != 0:
            return self.sections[-1].ends_at
        return None

    def get_gauge(self):
        if len(self.sections) != 0:
            return self.sections[0].gauge
        return None

    def has_warning(self):
        for section in self.sections:
            if len(section.warnings) > 0:
                return True
        return False

    # TODO continue adding constraints

    def __repr__(self):
        return f"Railway('{self.name}', '{self.starts_at}', '{self.ends_at}')"


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
    warnings = db.relationship("Warning", secondary="section_warning")

    __table_args__ = (
        db.UniqueConstraint(starts_at, ends_at, name="uq_starts_at_ends_at"),
        db.CheckConstraint(starts_at != ends_at, name="ck_starts_at_ends_at"),
    )


class Warning(db.Model):
    __tablename__ = "warning"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    sections = db.relationship("Section", secondary="section_warning")
    # section_id = db.Column(db.Integer, db.ForeignKey("section.id"), nullable=False)


# Association table for sections <-> warnings
class SectionWarning(db.Model):
    __tablename__ = "section_warning"
    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey("section.id"))
    warning_id = db.Column(db.Integer, db.ForeignKey("warning.id"))

    section = db.relationship("Section", backref=backref("section_warning", cascade="all, delete-orphan"))
    warning = db.relationship("Warning", backref=backref("section_warning", cascade="all, delete-orphan"))


# <------------------- MA Schemas --------------------->

# Station schema
class StationSchema(ma.Schema):
    class Meta:
        ordered = True
        fields = (
            'id',
            'name',
            'state'
        )


class WarningSchema(ma.Schema):
    class Meta:
        ordered = True
        fields = (
            'id',
            'title',
            'description',
        )


class SectionSchema(ma.Schema):
    class Meta:
        ordered = True
        fields = (
            'id',
            'start_station',
            'end_station',
            'length',
            'user_fee',
            'max_speed',
            'gauge',
            'railway_id',
            'warnings'
        )

    start_station = ma.Nested(StationSchema)
    end_station = ma.Nested(StationSchema)
    warnings = ma.Nested(WarningSchema, many=True)


class RailwaySchema(ma.Schema):
    class Meta:
        model = Railway
        ordered = True
        fields = (
            'id',
            'name',
            'start_station',
            'end_station',
            'sections'
        )

    start_station = ma.Nested(StationSchema)
    end_station = ma.Nested(StationSchema)
    sections = ma.Nested(SectionSchema, many=True)


class SectionWarningSchema(ma.Schema):
    class Meta:
        fields = (
            'id',
            'section_id',
            'warning_id'
        )


# Init schema
station_schema = StationSchema()  # use strict = True to avoid console warning
stations_schema = StationSchema(many=True)  # for multiple returns values

railway_schema = RailwaySchema()
railways_schema = RailwaySchema(many=True)

section_schema = SectionSchema()
sections_schema = SectionSchema(many=True)

warning_schema = WarningSchema()
warnings_schema = WarningSchema(many=True)
