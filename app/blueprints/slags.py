from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from app.db_connect import get_db
from app.functions import is_logged_in, submit_slag, get_leaderboard, update_slag, get_user_submissions, get_total_points, get_submission_details, get_accomplishment_id, get_all_accomplishments, get_submission_by_id_and_user
from pymysql.cursors import DictCursor

slags = Blueprint('slags', __name__)

@slags.route('/slag_submission', methods=['GET', 'POST'])
def slag_submission():
    if not is_logged_in():
        flash('Please log in to submit a SLAG.', 'warning')
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')

    if request.method == 'POST':
        # Get the form data
        accomplishment_type = request.form.get('accomplishment_type')
        proof_image = request.files.get('proof_image')

        if not accomplishment_type:
            flash('Please select an accomplishment type.', 'warning')
            return redirect(url_for('slags.slag_submission'))

        # Fetch the accomplishment_id for the selected type
        accomplishment = get_accomplishment_id(accomplishment_type)

        if not accomplishment:
            flash('Invalid accomplishment type selected.', 'danger')
            return redirect(url_for('slags.slag_submission'))

        accomplishment_id = accomplishment['accomplishment_id']

        # Call submit_slag function
        if submit_slag(user_id, accomplishment_id, proof_image):
            flash('SLAG submitted successfully!', 'success')
        else:
            flash('Error submitting SLAG. Please try again.', 'danger')

    # Fetch available accomplishment types and their points
    accomplishments = get_all_accomplishments()

    # Fetch user's existing SLAG submissions
    user_submissions = get_user_submissions(user_id)

    # Fetch the user's total points
    total_points = get_total_points(user_id)

    return render_template(
        'slag_submission.html',
        accomplishments=accomplishments,
        user_submissions=user_submissions,
        total_points=total_points
    )

@slags.route('/edit_slag/<int:submission_id>', methods=['GET', 'POST'])
def edit_slag(submission_id):
    if not is_logged_in():
        flash('Please log in to edit a SLAG.', 'warning')
        return redirect(url_for('auth.login'))

    submission = get_submission_details(submission_id)

    if not submission:
        flash('Submission not found.', 'danger')
        return redirect(url_for('slags.slag_submission'))

    if request.method == 'POST':
        accomplishment_type = request.form.get('accomplishment_type')
        proof_image = request.files.get('proof_image')

        accomplishment = get_accomplishment_id(accomplishment_type)

        if not accomplishment:
            flash('Invalid accomplishment type selected.', 'danger')
            return redirect(url_for('slags.edit_slag', submission_id=submission_id))

        accomplishment_id = accomplishment['accomplishment_id']

        if update_slag(submission_id, accomplishment_id, proof_image):
            flash('SLAG updated successfully!', 'success')
            return redirect(url_for('slags.slag_submission'))
        else:
            flash('Error updating SLAG. Please try again.', 'danger')

    accomplishments = get_all_accomplishments()
    user_id = session.get('user_id')
    user_submissions = get_user_submissions(user_id)
    total_points = get_total_points(user_id)

    return render_template(
        'slag_submission.html',
        submission=submission,
        accomplishments=accomplishments,
        user_submissions=user_submissions,
        total_points=total_points
    )

@slags.route('/delete_slag/<int:submission_id>', methods=['POST'])
def delete_slag(submission_id):
    if not is_logged_in():
        flash('Please log in to delete a SLAG.', 'warning')
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')

    submission = get_submission_by_id_and_user(submission_id, user_id)

    if not submission:
        flash('Submission not found or unauthorized action.', 'danger')
        return redirect(url_for('slags.slag_submission'))

    # Delete the submission
    db = get_db()
    cursor = db.cursor(DictCursor)

    cursor.execute("DELETE FROM slag_submissions WHERE submission_id = %s", (submission_id,))
    db.commit()

    return redirect(url_for('slags.slag_submission'))

@slags.route('/leaderboard')
def leaderboard():
    page = request.args.get('page', 1, type=int)
    leaderboard_data = get_leaderboard(page)

    return render_template('leaderboard.html', leaderboard_data=leaderboard_data)