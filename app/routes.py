#OS used to read the link from the file
import os
from flask import Flask, render_template, request, redirect, url_for
#SQLAlchemy used to create the database
from flask_sqlalchemy import SQLAlchemy
#Flask-Login used to manage the user login
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
#Flask-WTF used to create the forms
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
#Flask-Bcrypt used to hash the passwords
from flask_bcrypt import Bcrypt
try:
    from app import app as app, db, login_manager, bcrypt
except ImportError:
    from __init__ import app, db, login_manager, bcrypt

@app.before_first_request
def create_tables():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class Task(db.Model):
	__tablename__ = 'Task'
	id = db.Column(db.Integer,primary_key=True)
	title = db.Column(db.String(100), nullable=False)
	status = db.Column(db.String(50), nullable=False)
	uid = db.Column(db.String(20), nullable=False)


class RegisterForm(FlaskForm):
    '''Create with flask register from wtforms  to validate the form''' 
    username = StringField(validators=[
                           InputRequired()], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired()], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError('Opps it looks like that username is already taken :/')


class LoginForm(FlaskForm):
    """
    Create the log in form with flask to ease validation"""
    username = StringField(validators=[InputRequired()], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired()], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')


@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user:
			if bcrypt.check_password_hash(user.password, form.password.data):
				login_user(user)
				return redirect(url_for('homepage'))
		else:
			error = 'Opps it looks like that username or password is incorrect :/'
			return render_template('login.html', form=form, error=error)
	return render_template('login.html', form=form)


@app.route('/board', methods=['GET', 'POST'])
@login_required
def homepage():
	"""
	Main Board
	"""

	todo = Task.query.filter_by(status='todo',  uid=current_user.username).all()
	inprogress = Task.query.filter_by(status='inprogress',  uid=current_user.username).all()
	done = Task.query.filter_by(status='done',  uid=current_user.username).all()
	#return render_template('index.html')
	return render_template("index.html", todo=todo, inprogress=inprogress, done=done)

@app.route('/add', methods=['GET', 'POST'])
def add():
    """
    Add a new task
    """
    if request.method == 'POST':
        task = Task(title=request.form.get("title"), status='todo', uid=current_user.username)
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('homepage'))
    else:
        return redirect(url_for('homepage'))

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@ app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm()
	if form.validate_on_submit() == True:
		hashed_password = bcrypt.generate_password_hash(form.password.data)
		new_user = User(username=form.username.data, password=hashed_password)
		db.session.add(new_user)
		db.session.commit()
		return redirect(url_for('homepage'))
	else:
		error = 'Opps it looks like that username already exists :/'
		return render_template('register.html', form=form, error=error)
	return render_template('register.html', form=form)
	

@app.route("/delete",methods=['GET', 'POST'])
def delete():
    if request.method == 'POST':
            task = Task.query.filter_by(id=request.form.get("id")).first()
            db.session.delete(task)
            db.session.commit()
            return redirect(url_for('homepage'))
    else:
            return redirect(url_for('homepage'))
    

@app.route("/update_next", methods=['GET', 'POST'])
def update_next():
    if request.method == 'POST':
        task = Task.query.filter_by(id=request.form.get("id")).first()
        if task.status == "todo":
            task.status = "inprogress"
        elif task.status == "inprogress":
            task.status = "done"
        db.session.commit()
        return redirect(url_for('homepage'))
    else:
        return redirect(url_for('homepage'))
   

@app.route("/update_pre", methods=['GET', 'POST'])
def update_pre():
    if request.method == 'POST':
        task = Task.query.filter_by(id=request.form.get("id")).first()
        if task.status == "inprogress":
            task.status = "todo"
        elif task.status == "done":
            task.status = "inprogress"
        db.session.commit()
        return redirect(url_for('homepage'))
    else:
        return redirect(url_for('homepage'))
	

