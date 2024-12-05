from flask import render_template
from . import app

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/slag_submission')
def slag_submission():
    return render_template('slag_submission.html')

@app.route('/brother_catalog')
def brother_catalog():
    return render_template('brother_catalog.html')

@app.route('/update_slag')
def update_slag():
    return render_template('update_slag.html')

@app.route('/my_account')
def my_account():
    return render_template('my_account.html')