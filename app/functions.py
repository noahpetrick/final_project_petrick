import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.db_connect import get_db
from flask import session, current_app, g
from pymysql.cursors import DictCursor
import pandas as pd

def create_user(username, password, full_name, pledge_class_year, gpa, initiation_date, graduation_date):
    db = get_db()
    cursor = db.cursor()
    hashed_password = generate_password_hash(password)
    query = """
        INSERT INTO users (username, password, full_name, pledge_class_year, gpa, initiation_date, graduation_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (username, hashed_password, full_name, pledge_class_year, gpa, initiation_date, graduation_date))
    db.commit()

def check_user_credentials(username, password):
    db = get_db()
    cursor = db.cursor(DictCursor)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    return user if user and check_password_hash(user['password'], password) else None

def is_logged_in():
    return 'logged_in' in session and session['logged_in']

def submit_slag(user_id, accomplishment_id, proof_image=None):
    db = get_db()
    cursor = db.cursor()

    # Fetch points for the selected accomplishment
    cursor.execute("SELECT points FROM accomplishments WHERE accomplishment_id = %s", (accomplishment_id,))
    accomplishment = cursor.fetchone()

    if not accomplishment:
        print(f"Error: No points found for accomplishment_id {accomplishment_id}")
        return False

    points = accomplishment['points']  # Get the points value

    # Handle optional proof image
    image_filename = None
    if proof_image and proof_image.filename:
        image_filename = secure_filename(proof_image.filename)
        image_path = os.path.join(current_app.root_path, 'static/proof_images', image_filename)
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        proof_image.save(image_path)

    try:
        query = """
            INSERT INTO slag_submissions (user_id, accomplishment_id, proof_image, submission_date, points)
            VALUES (%s, %s, %s, NOW(), %s)
        """
        cursor.execute(query, (user_id, accomplishment_id, image_filename, points))
        db.commit()
        return True
    except Exception as e:
        print(f"Error submitting SLAG: {e}")
        db.rollback()
        return False
    finally:
        cursor.close()

def get_user_submissions(user_id):
    db = get_db()
    cursor = db.cursor(DictCursor)
    query = """
        SELECT s.submission_id, a.description AS accomplishment_description, s.proof_image
        FROM slag_submissions s
        JOIN accomplishments a ON s.accomplishment_id = a.accomplishment_id
        WHERE s.user_id = %s
    """
    cursor.execute(query, (user_id,))
    return cursor.fetchall()

def get_total_points(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT SUM(points) AS total_points
        FROM slag_submissions
        WHERE user_id = %s
    """, (user_id,))
    total_points = cursor.fetchone().get('total_points', 0) or 0
    cursor.close()
    return total_points

def get_submission_details(submission_id):
    db = get_db()
    cursor = db.cursor(DictCursor)
    query = """
        SELECT ss.*, a.description AS accomplishment_description
        FROM slag_submissions ss
        JOIN accomplishments a ON ss.accomplishment_id = a.accomplishment_id
        WHERE ss.submission_id = %s
    """
    cursor.execute(query, (submission_id,))
    return cursor.fetchone()

def get_accomplishment_id(accomplishment_type):
    db = get_db()
    cursor = db.cursor(DictCursor)
    query = "SELECT accomplishment_id FROM accomplishments WHERE description = %s"
    cursor.execute(query, (accomplishment_type,))
    return cursor.fetchone()

def get_all_accomplishments():
    db = get_db()
    cursor = db.cursor(DictCursor)
    query = "SELECT description, points FROM accomplishments"
    cursor.execute(query)
    return cursor.fetchall()

def update_slag(submission_id, accomplishment_id, proof_image=None):
    db = get_db()
    cursor = db.cursor()

    # Handle image upload if provided
    if proof_image:
        image_filename = secure_filename(proof_image.filename)
        image_path = os.path.join(current_app.root_path, 'static/proof_images', image_filename)
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        proof_image.save(image_path)
    else:
        image_filename = None

    # Update the submission in the database
    query = """
        UPDATE slag_submissions
        SET accomplishment_id = %s, proof_image = COALESCE(%s, proof_image)
        WHERE submission_id = %s
    """
    cursor.execute(query, (accomplishment_id, image_filename, submission_id))
    db.commit()
    cursor.close()
    return True

def get_submission_by_id_and_user(submission_id, user_id):
    db = get_db()
    cursor = db.cursor(DictCursor)
    cursor.execute("SELECT * FROM slag_submissions WHERE submission_id = %s AND user_id = %s", (submission_id, user_id))
    submission = cursor.fetchone()
    cursor.close()
    return submission

def get_leaderboard(page=1, per_page=10):
    db = get_db()
    cursor = db.cursor(DictCursor)
    offset = (page - 1) * per_page
    cursor.execute("""
        SELECT full_name, profile_image, total_points
        FROM leaderboard
        ORDER BY total_points DESC
        LIMIT %s OFFSET %s
    """, (per_page, offset))
    return cursor.fetchall()

def update_user_details(user_id, full_name, pledge_class_year, gpa, initiation_date, graduation_date, positions,
                        major_accomplishments):
    db = get_db()
    cursor = db.cursor()

    query = """
        UPDATE users
        SET full_name = %s, pledge_class_year = %s, gpa = %s, initiation_date = %s, graduation_date = %s, positions = %s, major_accomplishments = %s
        WHERE user_id = %s
    """

    # Ensure the positions are passed correctly as a string
    cursor.execute(query, (
    full_name, pledge_class_year, gpa, initiation_date, graduation_date, positions, major_accomplishments, user_id))
    db.commit()

def update_profile_image(user_id, profile_image):
    if profile_image:
        # Save the uploaded image to a specific directory
        image_filename = secure_filename(profile_image.filename)
        image_path = os.path.join(current_app.root_path, 'static/profile_images', image_filename)
        os.makedirs(os.path.dirname(image_path), exist_ok=True)  # Ensure the directory exists
        profile_image.save(image_path)

        # Update the user's profile image path in the database
        db = get_db()
        cursor = db.cursor()
        query = "UPDATE users SET profile_image = %s WHERE user_id = %s"
        cursor.execute(query, (image_filename, user_id))
        db.commit()
        cursor.close()
        return image_filename
    return None

def search_brothers_by_name(name_fragment):
    db = get_db()
    cursor = db.cursor(DictCursor)
    # Use ILIKE for case-insensitivity (if supported by your database; otherwise, use LOWER for compatibility)
    query = """
    SELECT user_id, full_name, profile_image 
    FROM users 
    WHERE LOWER(full_name) LIKE LOWER(%s)
    """
    # Add wildcards to the search term for partial matching
    search_term = f"%{name_fragment}%"
    cursor.execute(query, (search_term,))
    return cursor.fetchall()

def search_brothers_by_pledge_class_year(pledge_class_year):
    db = get_db()
    cursor = db.cursor(DictCursor)
    query = "SELECT user_id, full_name, profile_image FROM users WHERE pledge_class_year = %s"
    cursor.execute(query, (pledge_class_year,))
    return cursor.fetchall()

def get_brother_details(user_id):
    db = get_db()
    cursor = db.cursor(DictCursor)
    query = "SELECT * FROM users WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    return cursor.fetchone()

def load_user():
    if 'user_id' in session:
        db = get_db()
        cursor = db.cursor(DictCursor)
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (session['user_id'],))
        g.user = cursor.fetchone()
    else:
        g.user = None

def get_user_and_submissions(user_id):
    db = get_db()
    cursor = db.cursor(DictCursor)

    # Retrieve user information
    cursor.execute("SELECT user_id, username, full_name FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()

    # Retrieve submissions
    cursor.execute("""
        SELECT slag_submissions.submission_id, slag_submissions.points, accomplishments.description, slag_submissions.proof_image
        FROM slag_submissions
        JOIN accomplishments ON slag_submissions.accomplishment_id = accomplishments.accomplishment_id
        WHERE slag_submissions.user_id = %s
    """, (user_id,))
    submissions = cursor.fetchall()

    cursor.close()
    return user, submissions

def get_users_data(sort_by='full_name'):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
            SELECT users.user_id, users.username, users.full_name, users.pledge_class_year,
                   SUM(accomplishments.points) AS total_points,
                   MAX(slag_submissions.submission_date) AS recent_submission_date
            FROM users
            LEFT JOIN slag_submissions ON users.user_id = slag_submissions.user_id
            LEFT JOIN accomplishments ON slag_submissions.accomplishment_id = accomplishments.accomplishment_id
            GROUP BY users.user_id
        """)
    users_data = cursor.fetchall()
    cursor.close()

    # Convert to a pandas DataFrame for easy manipulation
    df = pd.DataFrame(users_data, columns=["user_id", "username", "full_name", "pledge_class_year", "total_points", "recent_submission_date"])

    if sort_by == 'name':
        df = df.sort_values('full_name')
    elif sort_by == 'pledge_class_year':
        df = df.sort_values('pledge_class_year')
    elif sort_by == 'total_points':
        df = df.sort_values('total_points', ascending=False)
    elif sort_by == 'recent_submission':
        df['recent_submission_date'] = pd.to_datetime(df['recent_submission_date'], errors='coerce')
        df = df.sort_values('recent_submission_date', ascending=False)

    sorted_users = df.to_dict(orient="records")

    for user in sorted_users:
        if pd.isna(user['recent_submission_date']):
            user['recent_submission_date'] = None

    return sorted_users