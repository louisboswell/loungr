from app import db
from app.models import User, Room, Post

def createUser(name, email, password):
        user = User(username = name, email=email)
        user.set_password(password)
        db.session.add(user)

createUser("Louis", "louis@gmail.com", "password")
createUser("Conor", "conor@gmail.com", "password")
createUser("Jack", "jack@gmail.com", "password")

users = User.query.all()

for user in users:
    print (user)
    print("follows")

    for follow in user.followed:
        print(follow)
    
    print("\n")

print(users)