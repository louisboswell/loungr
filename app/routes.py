from flask import render_template
from app import app

@app.route('/')
def base():
    return render_template('login.html')
    
@app.route('/index')
def index():
    return render_template('base.html')