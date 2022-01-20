from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy, event
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate

app = Flask(__name__)
app.config["SECRET_KEY"] = "3cd7d089a25376da2d10d0b88b429cd1"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///railway_system.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JSON_SORT_KEYS"] = False
# "sqlite:1_railway_system/resources/railway_system.db"
db = SQLAlchemy(app)
event.listen(db.engine, 'connect', lambda c, _: c.execute('pragma foreign_keys=on'))

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"


# Init ma
ma = Marshmallow(app)

from . import models

# Flask Migrate
migrate = Migrate(app, db)

from . import routes
