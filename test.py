import unittest
from unittest.mock import patch
import random
import string
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
from app import app, db, login_manager
from faker import Faker
from app import app as app, db, login_manager, bcrypt
from app.routes import User, Task

#Weaker testing of the user and password authetification
def new_user():
    fake = Faker()
    new_user = User(username= 'test', password=fake.password())
    db.session.add(new_user)
    db.session.commit()
    return new_user

class TestApp(unittest.TestCase):
    def setUp(self):
        with app.app_context():
            app.config['TESTING'] = True
            app.config['DEBUG'] = False
            self.app = app.test_client()
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_creation(self):
        with app.app_context():
            new_user()
            user = User.query.filter_by(username='test').first()
            self.assertEqual(user.username, 'test')

    def test_correct_login(self):
        with app.app_context(),  app.test_request_context():
            tester = app.test_client(self)
            new_user()
            user = User.query.filter_by(username='test').first()
            response = tester.post('/login',data = dict(username="test", password=user.password, login_form=""),follow_redirects=True)
            login_user(user)
            self.assertEqual(current_user.username, 'test')
            self.assertEqual(response.status_code, 200) 

    def test_add_samename_task(self):
        """
        Test assing a simple task.
        Basic add test to teh database
        """
        with app.app_context(),  app.test_request_context():
            tester = app.test_client(self)
            new_user()
            user = User.query.filter_by(username='test').first()
            login_user(user)
            new = Task(id = 1, title = 'tasktest', status = 'todo', uid=current_user.username)
            self.app.post('/add', data=dict(title='tasktest', uid = current_user.username), follow_redirects=True)
            task = Task.query.filter_by(title='tasktest').first()
            if task.id == 2:
                return True
            else:
                return False

    def test_different_user_tasks(self):
        """
        Checks if the same name can be used by different users
        """
        with app.app_context(),  app.test_request_context():
            tester = app.test_client(self)
            new_user()
            fake = Faker()
            user = User.query.filter_by(username='test').first()
            login_user(user)
            #new = Task(id = 1, title = 'tasktest', status = 'todo', uid=current_user.username)
            self.app.post('/add', data=dict(title='tasktest', uid=current_user.username), follow_redirects=True)
            task = Task.query.filter_by(title='tasktest').first()
            logout_user()
            user2 = User(username= 'new', password=fake.password())
            db.session.add(user2)
            db.session.commit()
            login_user(user2)
            self.app.post('/add', data=dict(title='tasktest', uid=current_user.username), follow_redirects=True)
            task2 = Task.query.filter_by(title='tasktest').first()
            if task.id !=  task2.id and task.uid != task2.uid:
                return True
            else:
                return False

    def test_add_random_task(self):
        """
        Checks the imput of tasks with random names

        Appends multiple random tasks to the database
        to check if the names are valid 
        """
        with app.app_context(),  app.test_request_context():
            tester = app.test_client(self)
            new_user()
            user = User.query.filter_by(username='test').first()
            login_user(user)
            self.app.post('/add', data=dict(title='tasktest', uid = current_user.username), follow_redirects=True)
            test = []
            for i in range(10):
                num = random.randint(1, 200)
                characters = string.ascii_letters + string.digits + string.punctuation
                newt  = str(''.join(random.choice(characters) for i in range(num)))
                self.app.post('/add', data=dict(title= newt, uid = current_user.username), follow_redirects=True)
                task = Task.query.filter_by(title= newt).first()
                if task.id == i+1:
                    test.append(True)
            if False not in test:
                return True

    def test_delete_task(self):
        """
        Checks that tasks are deleted

        Uses the title, assuming the creation of a new db
        """
        with app.app_context(),  app.test_request_context():
            tester = app.test_client(self)
            new_user()
            user = User.query.filter_by(username='test').first()
            login_user(user)
            self.app.post('/add', data=dict(title='tasktest', uid = current_user.username), follow_redirects=True)
            task = Task.query.filter_by(title='tasktest').first()
            self.app.post('/delete', data=dict(id=task.id), follow_redirects=True)
            task = Task.query.filter_by(title='tasktest').first()
            self.assertIsNone(task)
    

    def test_delete_self_name_task(self):
        """
        Checks that only the specified it's delated and not others with teh same name
        Checks with asserting id's and lenght of the final query


        """
        with app.app_context(),  app.test_request_context():
            tester = app.test_client(self)
            new_user()
            user = User.query.filter_by(username='test').first()
            login_user(user)
            self.app.post('/add', data=dict(title='tasktest', uid = current_user.username), follow_redirects=True)
            #self.app.post('/add', data=dict(title='tasktest', uid = current_user.username), follow_redirects=True)
            task1 = Task.query.filter_by(title='tasktest', uid = current_user.username).first()
            self.app.post('/add', data=dict(title='tasktest', uid = current_user.username), follow_redirects=True)
            task2 = Task.query.filter_by(title='tasktest', uid = current_user.username).first()
            if task1.id != task2.id:
                return True
            self.app.post('/delete',  data=dict(id=task1.id), follow_redirects=True)
            after = Task.query.filter_by(title='tasktest').all()
            #Becasue task1 was deleted task2 should be the only one with the name test
            task2 = Task.query.filter_by(title='tasktest').first()
            self.assertEqual(len(after), len([1]))
            self.assertEqual(task1.id, 1)
            self.assertEqual(task2.id, 2)


    def test_update_task_next(self):
        """
        Checks if the task was updated to the next columns
        """
        with app.app_context(),  app.test_request_context():
            tester = app.test_client(self)
            new_user()
            user = User.query.filter_by(username='test').first()
            login_user(user)
            self.app.post('/add', data=dict(title='tasktest', uid = current_user.username), follow_redirects=True)
            task = Task.query.filter_by(title='tasktest').first()
            self.app.post('/update_next', data=dict(id=task.id), follow_redirects=True)
            task = Task.query.filter_by(title='tasktest').first()
            self.assertEqual(task.status, 'inprogress')
        
    def test_update_task_pre(self):
        """
        Checks if the task was updated to the next columns
        """
        with app.app_context(),  app.test_request_context():
            tester = app.test_client(self)
            new_user()
            user = User.query.filter_by(username='test').first()
            login_user(user)
            self.app.post('/add', data=dict(title='tasktest', uid = current_user.username), follow_redirects=True)
            task = Task.query.filter_by(title='tasktest').first()
            self.app.post('/update_pre', data=dict(id=task.id), follow_redirects=True)
            task = Task.query.filter_by(title='tasktest').first()
            self.assertEqual(task.status, 'todo')

    def test_wrong_method_update(self):
        """
        Test that the page dosen't charsh if the wrong url is called
        """
        with app.app_context(),  app.test_request_context():
            tester = app.test_client(self)
            new_user()
            user = User.query.filter_by(username='test').first()
            login_user(user)
            response = self.app.get('/update_next', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            response = self.app.get('/update_pre', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

    def test_wrong_method_delete(self):
        """
        Test that the page dosen't charsh if the wrong url is called
        """
        with app.app_context(),  app.test_request_context():
            tester = app.test_client(self)
            new_user()
            user = User.query.filter_by(username='test').first()
            login_user(user)
            response = self.app.get('/delete', follow_redirects=True)
            self.assertEqual(response.status_code, 200)


        

if __name__ == '__main__':
    unittest.main()
