from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from app.db_connect import get_db
from app.functions import is_logged_in, update_user_details, update_profile_image
import os
from werkzeug.utils import secure_filename
from pymysql.cursors import DictCursor

users = Blueprint('users', __name__)

@users.route('/my_account', methods=['GET', 'POST'])
def my_account():
    if not is_logged_in():
        flash('Please log in to view your account.', 'warning')
        return redirect(url_for('auth.login'))

    db = get_db()
    cursor = db.cursor(DictCursor)
    user_id = session.get('user_id')

    if request.method == 'POST':
        # Update profile details
        full_name = request.form.get('full_name')
        pledge_class_year = request.form.get('pledge_class_year')
        gpa = request.form.get('gpa')
        initiation_date = request.form.get('initiation_date')
        graduation_date = request.form.get('graduation_date')

        # Handle positions as a comma-separated string
        positions = ', '.join(request.form.getlist('positions'))

        # Get major accomplishments and use an empty string if none provided
        major_accomplishments = request.form.get('major_accomplishments', '')

        try:
            update_user_details(user_id, full_name, pledge_class_year, gpa, initiation_date, graduation_date, positions,
                                major_accomplishments)
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            flash(f'Error updating profile: {str(e)}', 'danger')

    # Fetch user details for display
    query = "SELECT * FROM users WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()

    return render_template('my_account.html', user=user)

@users.route('/update_profile_image', methods=['POST'])
def update_profile_image_route():
    if not is_logged_in():
        flash('Please log in to update your profile image.', 'warning')
        return redirect(url_for('auth.login'))

    if 'profile_image' not in request.files:
        flash('No image selected for upload.', 'danger')
        return redirect(url_for('users.my_account'))

    profile_image = request.files['profile_image']

    if profile_image.filename == '':
        flash('No selected file.', 'danger')
        return redirect(url_for('users.my_account'))

    if profile_image:
        # Save the image
        filename = secure_filename(profile_image.filename)
        image_path = os.path.join('static/profile_images', filename)
        profile_image.save(image_path)

        try:
            # Update profile image path in the database
            update_profile_image(session['user_id'], image_path)
            flash('Profile image updated successfully!', 'success')
        except Exception as e:
            flash(f'Error updating profile image: {str(e)}', 'danger')

    return redirect(url_for('users.my_account'))

@users.route('/my_account_edit', methods=['GET', 'POST'])
def my_account_edit():
    if not is_logged_in():
        flash('Please log in to edit your account.', 'warning')
        return redirect(url_for('auth.login'))

    db = get_db()
    cursor = db.cursor(DictCursor)
    user_id = session.get('user_id')

    # Fetch user details for editing
    query = "SELECT * FROM users WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()

    if request.method == 'POST':
        # Retrieve form data
        full_name = request.form.get('full_name')
        pledge_class_year = request.form.get('pledge_class_year')
        gpa = request.form.get('gpa')
        initiation_date = request.form.get('initiation_date')
        graduation_date = request.form.get('graduation_date')
        positions = request.form.get('positions')
        major_accomplishments = request.form.get('major_accomplishments')

        profile_image = request.files.get('profile_image')
        if profile_image and profile_image.filename != '':
            update_profile_image(user_id, profile_image)  # Pass the profile_image object

        try:
            # Call the function to update the details in the database
            update_user_details(user_id, full_name, pledge_class_year, gpa, initiation_date, graduation_date, positions, major_accomplishments)
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('users.my_account'))
        except Exception as e:
            flash(f'Error updating profile: {str(e)}', 'danger')

    return render_template('my_account_edit.html', user=user)