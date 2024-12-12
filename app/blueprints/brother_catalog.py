from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.functions import search_brothers_by_name, search_brothers_by_pledge_class_year, get_brother_details, get_total_points

brother_catalog = Blueprint('brother_catalog', __name__)

@brother_catalog.route('/brothers', methods=['GET', 'POST'])
def brothers():
    results = []  # Initialize as an empty list
    if request.method == 'POST':
        search_term = request.form.get('search_term', '').strip()

        # Perform database query based on search_type
        if search_term:
            results_by_name = list(search_brothers_by_name(search_term))
            results_by_pledge_class_year = list(search_brothers_by_pledge_class_year(search_term))
            results = results_by_name + results_by_pledge_class_year

    return render_template('brother_catalog.html', results=results)

@brother_catalog.route('/brother_detail/<int:user_id>')
def brother_detail(user_id):
    brother = get_brother_details(user_id)
    if not brother:
        return 'Brother not found.', 404

    total_points = get_total_points(user_id)
    return render_template('brother_detail.html', brother=brother, total_points=total_points)