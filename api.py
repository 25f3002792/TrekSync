from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Trek, Booking, User

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/treks')
def get_treks():
    treks = Trek.query.all()
    return jsonify([{
        'id': t.id,
        'name': t.name,
        'location': t.location,
        'difficulty': t.difficulty,
        'available_slots': t.available_slots,
        'status': t.status
    } for t in treks])

@api_bp.route('/bookings')
@login_required
def get_bookings():
    if current_user.role == 'admin':
        bookings = Booking.query.all()
    else:
        bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': b.id,
        'user': b.user.username,
        'trek': b.trek.name,
        'status': b.status,
        'booking_date': b.booking_date.isoformat()
    } for b in bookings])