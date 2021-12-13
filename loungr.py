from app import app, db
from app.models import User, Post

if __name__ == '__main__':
    app.run(debug = True)