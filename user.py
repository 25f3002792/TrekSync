from flask import Blueprint, abort, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Trek, Booking
from forms import UserProfileForm
from datetime import datetime

user_bp = Blueprint('user', __name__)

def user_required():
    if not current_user.is_authenticated or current_user.role != 'user':
        abort(403)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    user_required()
    available_treks = Trek.query.filter(Trek.status == 'Open', Trek.available_slots > 0).all()
    booked = Booking.query.filter_by(user_id=current_user.id).all()
    booked_treks = [b.trek for b in booked if b.status == 'Booked']
    return render_template('user/dashboard.html', available_treks=available_treks, booked_treks=booked_treks)

@user_bp.route('/treks')
@login_required
def treks():
    user_required()
    search = request.args.get('search', '')
    difficulty = request.args.get('difficulty', '')
    location = request.args.get('location', '')
    query = Trek.query.filter(Trek.status == 'Open')
    if search:
        query = query.filter(Trek.name.ilike(f'%{search}%'))
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if location:
        query = query.filter(Trek.location.ilike(f'%{location}%'))
    treks = query.all()
    return render_template('user/treks.html', treks=treks, search=search, difficulty=difficulty, location=location)

@user_bp.route('/book/<int:trek_id>', methods=['POST'])
@login_required
def book_trek(trek_id):
    user_required()
    trek = Trek.query.get_or_404(trek_id)
    if trek.status != 'Open':
        flash('Trek is not open for booking.', 'danger')
        return redirect(url_for('user.treks'))
    if trek.available_slots <= 0:
        flash('No slots available.', 'danger')
        return redirect(url_for('user.treks'))
    existing = Booking.query.filter_by(user_id=current_user.id, trek_id=trek.id).first()
    if existing:
        flash('You have already booked this trek.', 'warning')
        return redirect(url_for('user.bookings'))
    booking = Booking(user_id=current_user.id, trek_id=trek.id, status='Booked')
    trek.available_slots -= 1
    db.session.add(booking)
    db.session.commit()
    flash('Trek booked successfully!', 'success')
    return redirect(url_for('user.bookings'))

@user_bp.route('/bookings')
@login_required
def bookings():
    user_required()
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_date.desc()).all()
    return render_template('user/bookings.html', bookings=bookings)

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_required()
    form = UserProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.email = form.email.data
        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('user.profile'))
    return render_template('user/profile.html', form=form)

@user_bp.route('/cancel-booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    user_required()
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('user.bookings'))
    if booking.status != 'Booked':
        flash('Booking cannot be cancelled.', 'warning')
        return redirect(url_for('user.bookings'))
    trek = booking.trek
    trek.available_slots += 1
    booking.status = 'Cancelled'
    db.session.commit()
    flash('Booking cancelled.', 'success')
    return redirect(url_for('user.bookings'))