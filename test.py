from app import models, db

user = models.User.query.all()
user = user[0]

room = models.Room()
room.new_room()

room2 = models.Room()
room2.new_room()

user.join_room(room)
print(user.is_member(room))
print(user.is_member(room2))

print(user.user_rooms())
print(type(user.user_rooms()))