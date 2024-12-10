from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.functions import create_user, check_user_credentials

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check user credentials (assuming this function now also fetches 'is_admin')
        user = check_user_credentials(username, password)
        if user:
            session['logged_in'] = True
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['is_admin'] = user.get('is_admin', False)  # Store admin status in session
            print(session)
            flash('Login successful!', 'success')

            # Redirect based on admin status
            if session['is_admin']:
                return redirect(url_for('admin.view_users'))  # Replace with your admin route
            else:
                return redirect(url_for('index'))  # Replace with your regular user route
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@auth.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        pledge_class_year = request.form['pledge_class_year']
        gpa = request.form['gpa']
        initiation_date = request.form['initiation_date']
        graduation_date = request.form['graduation_date']

        try:
            create_user(username, password, full_name, pledge_class_year, gpa, initiation_date, graduation_date)
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Error creating account: {str(e)}', 'danger')

    return render_template('create_account.html')