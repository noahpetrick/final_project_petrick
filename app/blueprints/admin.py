import pandas as pd
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.db_connect import get_db
from app.functions import get_users_data, get_user_and_submissions

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.before_request
def admin_check():
    if not session.get('is_admin', False):  # Replace with your admin-check logic
        flash('You do not have access to this page.')
        return redirect(url_for('auth.login'))

@admin.route('/users')
def view_users():
    sort_by = request.args.get('sort_by', 'full_name')
    sorted_users = get_users_data(sort_by)
    return render_template('admin.html', users=sorted_users, pd=pd)

@admin.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
    db.commit()
    flash('User deleted successfully.')
    return redirect(url_for('admin.view_users'))

@admin.route('/users/<int:user_id>/view_submissions')
def view_user_submissions(user_id):
    user, submissions = get_user_and_submissions(user_id)
    return render_template('user_submissions.html', submissions=submissions, user=user)

@admin.route('/submissions/<int:submission_id>/delete', methods=['POST'])
def delete_submission(submission_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM slag_submissions WHERE submission_id = %s", (submission_id,))
    db.commit()
    flash('SLAG submission deleted successfully.')
    return redirect(request.referrer or url_for('admin.view_users'))