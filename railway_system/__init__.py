from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["SECRET_KEY"] = "3cd7d089a25376da2d10d0b88b429cd1"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///railway_system.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# "sqlite:1_railway_system/resources/railway_system.db"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

# Init ma
ma = Marshmallow(app)

from . import routes



