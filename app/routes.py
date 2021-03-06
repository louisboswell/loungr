from flask import render_template, flash, redirect, url_for, request, jsonify
from flask.ctx import copy_current_request_context
from flask_sqlalchemy import model
from app import app, db, admin
from app.forms import CreateRoomForm, LoginForm, PostForm, RegistrationForm, EditProfileForm, EmptyForm, ChangePasswordForm, ReportForm, ReplyForm, SearchForm
from flask_login import current_user, login_user, login_required, logout_user
from wtforms.validators import ValidationError
from app.models import Post, User, Room, Reply
from werkzeug.urls import url_parse
from datetime import datetime
from flask_admin.contrib.sqla import ModelView

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Post, db.session))
admin.add_view(ModelView(Room, db.session))


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))

    rooms = current_user.user_rooms()
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Home', form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url, rooms = rooms)


@app.route('/post/<id>', methods=['GET', 'POST'])
@login_required
def post(id):
    post = Post.query.filter_by(id=id).first_or_404()
    form = ReplyForm()
    """
    if form.validate_on_submit():
        reply = Reply(body=form.body.data, user_id=current_user, post_id=post.id)
        db.session.add(reply)
        db.session.commit()
        return redirect(url_for('index'))
    """ 

    return render_template('post.html', post=post, form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('login'))
        
        login_user(user, remember=form.remember_me.data)
        app.logger.info("User %s logged in", user.username)

        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')

        return redirect(next_page)


    return render_template('login.html', form=form, title='Login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return(redirect(url_for('index')))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(username = form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)

        # Fixed error following user 1 afaik???
        for x in user.followed:
            user.followed.remove(x)

        db.session.commit()
        app.logger.info("User %s registered in", user.username)

        return redirect(url_for('login'))
    return render_template('register.html', form=form, title = 'Register')

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()

    following = user.count_following()
    followers = user.count_followers()
    rooms = len(user.user_rooms())
    num_posts = user.posts.count()

    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form, following=following,followers=followers, rooms = rooms, num_posts=num_posts, title=user.username)

@app.route('/leaderboard', methods=['GET', 'POST'])
@login_required
def leaderboard():
    users = User.query.all()
    no_users = len(users)

    return render_template('leaderboard.html', users=users, no_users=no_users, title='Leaderboard')

@app.route('/room/<id>')
@login_required
def room(id):
    room = Room.query.filter_by(id=id).first_or_404()
    members = room.get_members()

    app.logger.info("User %s viewed room id:%s successfully.", current_user.username, id)

    return render_template('room.html', room=room, members=members, user=current_user, title=room.name)

@app.route('/deleteroom/<id>')
@login_required
def deleteroom(id):
    room = Room.query.filter_by(id=id).first()

    if room is None:
        app.logger.warning("User %s tried to delete room id:%s which doesn't exist.", current_user.username, id)
        return redirect(url_for('rooms'))

    form = EmptyForm()

    if room.admin != current_user.id:
        return redirect(url_for('rooms'))

    if form.validate_on_submit:
        db.session.delete(room)
        db.session.commit()
        app.logger.info("User %s deleted room id:%s.", current_user.username, id)



    return render_template('deleteroom.html', room=room, form=form, title='Delete room?')

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():

    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your profile has been updated.')
        app.logger.info("User %s edited profile.", current_user.username)

        return redirect(url_for('edit_profile'))
    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    
    return render_template('edit_profile.html', form=form, title = 'Edit Profile')

@app.route('/changepassword', methods= ['GET','POST'])
@login_required
def changepassword():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=current_user.username).first()

        if user is None or not user.check_password(form.old_password.data):
            return redirect(url_for('edit_profile'))
        
        if form.new_password_1.data == form.new_password_2.data:
            user.set_password(form.new_password_1.data)
            db.session.commit()
            app.logger.info("User %s changed password.", current_user.username)

            
            return redirect(url_for('edit_profile'))

            

    return render_template('changepassword.html', form=form, title='Change password')


@app.route('/logout')
def logout():
    app.logger.info("User %s logged out.", current_user.username)

    logout_user()

    return redirect(url_for('index'))

@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()

        if user is None:
            flash('User {} not found.'.format(username))
            app.logger.warning("User %s failed to followed user %s.", current_user.username, username)
            return redirect(url_for('index'))

        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user', username=username))

        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(username))
        app.logger.info("User %s followed user %s.", current_user.username, username)

        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()

        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
            app.logger.warning("User %s failed to unfollow user %s.", current_user.username, username)


        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        app.logger.info("User %s  unfollowed user %s.", current_user.username, username)


        flash('You are not following {}.'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@app.route('/rooms')
@login_required
def rooms():
    rooms = current_user.user_rooms()
    no_rooms = len(rooms)
    return render_template('rooms.html', rooms = rooms, no_rooms = no_rooms, title='Your Rooms')

@app.route('/createroom', methods = ['GET', 'POST'])
@login_required
def createroom():
    form = CreateRoomForm()
    if form.validate_on_submit():

        temp = Room()
        temp.new_room(current_user)
        temp.set_name(form.name.data)
        temp.set_desc(form.desc.data)
        db.session.commit()

        app.logger.info("User %s created room id %s.", current_user.username, temp.id)

        flash('{} has been created.'.format(form.name.data))
        return redirect(url_for('rooms'))

    return render_template('createroom.html', form=form, title = 'Create Room')

@app.route('/join/<id>', methods=['GET', 'POST'])
@login_required
def join(id):
    room = Room.query.filter_by(id = id).first()
    current_user.join_room(room)
    db.session.commit()

    app.logger.info("User %s joined room id %s.", current_user.username, id)


    return redirect(url_for('rooms'))

@app.route('/leave/<id>', methods=['GET', 'POST'])
@login_required
def leave(id):
    room = Room.query.filter_by(id = id).first()
    current_user.leave_room(room)
    db.session.commit()

    app.logger.info("User %s left room id %s.", current_user.username, id)

    return redirect(url_for('rooms'))

@app.route('/rooms/all', methods=['GET', 'POST'])
@login_required
def allrooms():
    all_rooms = Room.query.all()
    no_rooms = len(all_rooms)

    no_user_rooms = len(current_user.user_rooms())
    rooms = current_user.user_rooms()
    return render_template('allrooms.html', rooms = rooms, no_rooms= no_rooms, no_user_rooms=no_user_rooms, all_rooms =all_rooms, title='All Rooms')

@app.route('/like/<int:post_id>/<action>')
@login_required
def like_action(post_id, action):
    post = Post.query.filter_by(id=post_id).first_or_404()

    if action == 'like':
        current_user.like_post(post)
        db.session.commit()
        app.logger.info("User %s disliked post id %s.", current_user.username, post_id)


    if action == 'unlike':
        current_user.unlike_post(post)
        db.session.commit()
        app.logger.info("User %s liked post id %s.", current_user.username, post_id)


    return redirect(request.referrer)

@app.route('/report/<int:post_id>', methods=['GET', 'POST'])
@login_required
def report_action(post_id):
    post = Post.query.filter_by(id = post_id).first_or_404()
    form = ReportForm()

    if form.validate_on_submit():
        app.logger.info("User %s reported post id %s, with report body: %s", current_user.username, post_id, form.report_desc.data)

        return redirect(url_for('index'))

    return render_template('report.html', post=post, form=form, title="Report Post")