from flask import render_template, redirect, session, url_for
from . import app
from app.functions import get_leaderboard

@app.route('/')
def index():
    if not session.get('logged_in', False):
        return redirect(url_for('auth.login'))

    # Fetch top-ranked brothers (all for the leaderboard)
    leaderboard_data = get_leaderboard(per_page=100)  # Adjust the per_page as needed

    # Separate top 3 and remaining brothers
    top_3 = leaderboard_data[:3] if len(leaderboard_data) >= 3 else leaderboard_data
    remaining = leaderboard_data[3:] if len(leaderboard_data) > 3 else []

    # Pass all necessary data to the template
    return render_template('index.html', top_3=top_3, remaining=remaining)

@app.route('/greetings')
def greetings():
    return render_template('greetings.html')

@app.context_processor
def inject_is_logged_in():
    return {'is_logged_in': session.get('logged_in', False)}

