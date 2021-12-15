import os
import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import app, db, models

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object(Config)
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        #the basedir lines could be added like the original db
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app = app.test_client()
        db.create_all()
        pass

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # USER TESTS FOR LOUNGR
    def test_createuser(self):
        user = User(username = form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)