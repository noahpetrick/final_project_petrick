from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.functions import search_brothers_by_name, search_brothers_by_pledge_class_year, get_brother_details, get_total_points

brother_catalog = Blueprint('brother_catalog', __name__)

@brother_catalog.route('/brothers', methods=['GET', 'POST'])
def brothers():
    results = []  # Initialize as an empty list
    if request.method == 'POST':
        search_term = request.form.get('search_term', '').strip()
        search_type = request.form.get('search_type', '').strip()

        # Perform database query based on search_type
        if search_type == 'name_fragment':
            results = search_brothers_by_name(search_term)
        elif search_type == 'pledge_class_year':
            results = search_brothers_by_pledge_class_year(search_term)

    return render_template('brother_catalog.html', results=results)

@brother_catalog.route('/brother_detail<int:user_id>')
def brother_detail(user_id):
    # Fetch brother's details
    brother = get_brother_details(user_id)

    if not brother:
        flash('Brother not found.', 'danger')
        return redirect(url_for('brother_catalog.brothers'))

    total_points = get_total_points(user_id)

    return render_template('brother_detail.html', brother=brother, total_points=total_points)