from flask import Blueprint, abort, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Trek, Booking, TrekStaffAssignment
from forms import StaffUpdateForm

staff_bp = Blueprint('staff', __name__)

def staff_required():
    if not current_user.is_authenticated or current_user.role != 'staff':
        abort(403)
    if not current_user.staff_profile or not current_user.staff_profile.approved:
        abort(403)
        
@staff_bp.route('/dashboard')
@login_required
def dashboard():
    staff_required()
    profile = current_user.staff_profile
    assignments = TrekStaffAssignment.query.filter_by(staff_id=profile.id).all()
    treks = [ass.trek for ass in assignments]
    trek_data = []
    for trek in treks:
        booked_count = Booking.query.filter_by(trek_id=trek.id, status='Booked').count()
        trek_data.append({'trek': trek, 'booked_count': booked_count})
    return render_template('staff/dashboard.html', trek_data=trek_data)

@staff_bp.route('/trek/<int:trek_id>', methods=['GET', 'POST'])
@login_required
def manage_trek(trek_id):
    staff_required()
    trek = Trek.query.get_or_404(trek_id)
    profile = current_user.staff_profile
    assignment = TrekStaffAssignment.query.filter_by(trek_id=trek.id, staff_id=profile.id).first()
    if not assignment:
        flash('You are not assigned to this trek.', 'danger')
        return redirect(url_for('staff.dashboard'))
    form = StaffUpdateForm(obj=trek)
    if form.validate_on_submit():
        if form.available_slots.data is not None:
            trek.available_slots = form.available_slots.data
        if form.status.data:
            trek.status = form.status.data
        db.session.commit()
        flash('Trek details updated successfully.', 'success')
        return redirect(url_for('staff.manage_trek', trek_id=trek.id))
    bookings = Booking.query.filter_by(trek_id=trek.id).all()
    return render_template('staff/manage_trek.html', trek=trek, form=form, bookings=bookings)

@staff_bp.route('/trek/<int:trek_id>/participants')
@login_required
def participants(trek_id):
    staff_required()
    trek = Trek.query.get_or_404(trek_id)
    profile = current_user.staff_profile
    assignment = TrekStaffAssignment.query.filter_by(trek_id=trek.id, staff_id=profile.id).first()
    if not assignment:
        flash('You are not assigned to this trek.', 'danger')
        return redirect(url_for('staff.dashboard'))
    bookings = Booking.query.filter_by(trek_id=trek.id).all()
    return render_template('staff/participants.html', trek=trek, bookings=bookings)