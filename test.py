import os
import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import app, db, models
from app.models import User, Post, Room
from config import Config

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

    user1 = User(username = "user1", email="user1@gmail.com")
    user1.set_password("user1")
    db.session.add(user1)
    
    user2 = User(username = "user2", email="user1@gmail.com")
    user2.set_password("user2")
    db.session.add(user2)

    print(User.query.all())

    # USER TESTS FOR LOUNGR

    # CREATE USER
    def test_createuser(self):
        user3 = User(username = "user2", email="user1@gmail.com")
        user3.set_password("user2")
        db.session.add(user3)

        self.assertEqual(len(User.query.all()), 3)
        pass

    # FOLLOW USER
    def test_followuser(self):
        pass

    # UNFOLLOW USER
    def test_unfollowuser(self):
        pass

    # LIKE POST
    def test_likepost(self):
        pass

    # UNLIKE POST
    def test_unlikepost(self):
        pass

    # CREATE ROOM
    def test_createroom(self):
        pass

    # JOIN ROOM
    def test_joinroom(self):
        pass

    # REPORT POST
    def test_reportpost(self):
        pass
    
    # LOGIN USER
    def test_loginuser(self):
        pass

if __name__ == '__main__':
    unittest.main()  