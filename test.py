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
        basedir = os.path.abspath(os.path.dirname(__file__))
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        db.create_all()

        # Clear test database
        User.query.delete()
        Post.query.delete()
        Room.query.delete()

        # Create 3 users for testing
        user1 = User(username = "user1", email="user1@gmail.com")
        user1.set_password("user1")
        db.session.add(user1)
        
        user2 = User(username = "user2", email="user2@gmail.com")
        user2.set_password("user2")
        db.session.add(user2)

        user3 = User(username = "user3", email="user3@gmail.com")
        user3.set_password("user3")
        db.session.add(user3)
        pass

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # USER TESTS FOR LOUNGR

    # CREATE USER
    def test_createuser(self):
        user3 = User(username = "user4", email="user4@gmail.com")
        user3.set_password("user4")
        db.session.add(user3)

        self.assertEqual(len(User.query.all()), 4)
        pass

    # FOLLOW USER
    def test_followuser(self):
        users = User.query.all()

        users[0].follow(users[1])
        db.session.commit()

        self.assertTrue(users[0] in users[1].followers)
        pass

    # UNFOLLOW USER
    def test_unfollowuser(self):
        users = User.query.all()

        users[0].unfollow(users[1])
        db.session.commit()

        self.assertTrue(users[0] not in users[1].followers)
        pass

    # CREATE POST
    def test_createpost(self):
        users = User.query.all()

        post = Post(body="Test post", author=users[0])
        db.session.add(post)
        db.session.commit()

        self.assertTrue((post in Post.query.all()) and post.author == users[0])
        pass

    # LIKE POST
    def test_likepost(self):
        users = User.query.all()

        post = Post(body="Test post", author=users[0])
        db.session.add(post)
        db.session.commit()

        posts = Post.query.all()

        users[0].like_post(posts[0])
        self.assertTrue(users[0].has_liked_post(posts[0]))
        pass

    # UNLIKE POST
    def test_unlikepost(self):
        users = User.query.all()

        post = Post(body="Test post", author=users[0])
        db.session.add(post)
        db.session.commit()

        posts = Post.query.all()

        users[0].unlike_post(posts[0])
        self.assertFalse(users[0].has_liked_post(posts[0]))
        pass

    # CREATE ROOM
    def test_createroom(self):
        users = User.query.all()

        temp = Room()
        temp.new_room(users[0])
        temp.set_name("test room")
        temp.set_desc("room users for testing")

        db.session.commit()

        self.assertTrue(temp in Room.query.all())
        pass

    # JOIN ROOM
    def test_joinroom(self):
        users = User.query.all()

        temp = Room()
        temp.new_room(users[0])
        temp.set_name("test room")
        temp.set_desc("room users for testing")

        db.session.commit()

        users[0].join_room(temp)
        self.assertTrue(users[0] in temp.get_members())
        pass

    # LEAVE ROOM
    def test_leaveroom(self):
        users = User.query.all()

        temp = Room()
        temp.new_room(users[0])
        temp.set_name("test room")
        temp.set_desc("room users for testing")

        db.session.commit()

        users[0].join_room(temp)
        users[0].leave_room(temp)
        self.assertTrue(users[0] not in temp.get_members())
        pass

    # REPORT POST
    def test_reportpost(self):
        users = User.query.all()


        post = Post(body="Test post", author=users[0])
        db.session.add(post)
        db.session.commit()
        posts = Post.query.all()

        response = self.app.get('/report/' + str(posts[0].id),
                               follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        pass
    
    # LOGIN USER
    def test_loginuser(self):
        response = self.app.get('/login',
                               follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        pass

if __name__ == '__main__':
    unittest.main()  