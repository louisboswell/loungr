from datetime import datetime
from enum import unique
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from flask_login import UserMixin
from hashlib import md5
from uuid import uuid4

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

# USER <-> ROOM RELATIONSHIP
members = db.Table('members', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('room_id', db.String(8), db.ForeignKey('room.id'))
)
# POST <-> USER RELATIONSHIP

# USER <-> LIKE RELATIONSHIP
class PostLike(db.Model):
    __tablename__ = 'post_like'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    posts = db.relationship('Post', backref='author', lazy='dynamic')
    replies = db.relationship('Reply', backref='author', lazy='dynamic')
    
    about_me = db.Column(db.String(140))    
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    followed = db.relationship(
        'User', secondary = followers,
        primaryjoin = (followers.c.follower_id == id),
        secondaryjoin = (followers.c.followed_id == id),
        backref = db.backref('followers', lazy='dynamic'), lazy='dynamic')

    liked = db.relationship(
    'PostLike',
    foreign_keys='PostLike.user_id',
    backref='user', lazy='dynamic')

    rooms = db.relationship('Room', secondary=members)

    def like_post(self, post):
        if not self.has_liked_post(post):
            like = PostLike(user_id=self.id, post_id=post.id)
            db.session.add(like)

    def unlike_post(self, post):
        if self.has_liked_post(post):
            PostLike.query.filter_by(
                user_id=self.id,
                post_id=post.id).delete()

    def has_liked_post(self, post):
        return PostLike.query.filter(
            PostLike.user_id == self.id,
            PostLike.post_id == post.id).count() > 0

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def count_following(self):
        return self.followed.count()

    def count_followers(self):
        return self.followers.count()

    """
    def followers(self):
        followers = []

        for user in User.query.all():
            if user.is_following(self):
                followers.append(user)

        return len(followers)
    """


    def is_following(self, user):
        # Should return a bool
        return user in self.followed

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def __repr__(self):
        return '<User {}>'.format(self.username)


    def join_room(self, room):
        if room not in self.rooms:
            self.rooms.append(room)

    def leave_room(self, room):
        if room in self.rooms:
            self.rooms.remove(room)

    def user_rooms(self):
        return self.rooms


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # NOT USED
    room_id = db.Column(db.String(8), db.ForeignKey('room.id'))

    likes = db.relationship('PostLike', backref='post', lazy='dynamic')
    replies = db.relationship('Reply', backref='reply', lazy='dynamic')

    def set_room(self, room):
        self.room_id = room

    def __repr__(self):
        return '<Post {}>'.format(self.body)

class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body= db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    

# TO IMPLEMENT
class Room(db.Model):
    id = db.Column(db.String(8), primary_key=True)
    name = db.Column(db.String(40), unique=True)
    desc = db.Column(db.String(250))
    admin = db.Column(db.Integer)
    # https://stackoverflow.com/questions/13484726/safe-enough-8-character-short-unique-random-string

    def new_room(self, user):
        # Generate short room code
        code = str(uuid4())[:8]
        self.id = code
        user.join_room(self)
        self.admin = user.id
    
    def set_name(self, name):
        self.name = name

    def set_desc(self, desc):
        self.desc = desc


    def get_members(self):
        users = User.query.all()
        correct = []

        for user in users:
            if self in user.rooms:
                correct.append(user)
        
        return correct



    def __repr__(self):
        return '<Room {}>'.format(self.id)



@login.user_loader
def load_user(id):
    return User.query.get(int(id))