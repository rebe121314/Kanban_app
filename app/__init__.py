import os
#from flask import Flask, render_template, url_for, redirect, g, request
from flask import Flask, render_template, request, redirect, url_for, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

project_dir = os.path.dirname(os.path.abspath(__file__))
# Create the database file in the project directory
database_file = "sqlite:///{}".format(os.path.join(project_dir, "database.db"))


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config['SECRET_KEY'] = 'thisisasecretkey'
db = SQLAlchemy(app)
db.init_app(app)
bcrypt = Bcrypt(app)



login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from app import routes