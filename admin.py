from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import db, User, StaffProfile, Trek, Booking, TrekStaffAssignment
from forms import TrekForm, StaffUpdateForm
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

def admin_required():
    if not current_user.is_authenticated or current_user.role != 'admin':
        abort(403)

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    admin_required()
    total_treks = Trek.query.count()
    total_users = User.query.filter_by(role='user').count()
    total_staff = User.query.filter_by(role='staff').count()
    total_bookings = Booking.query.count()
    return render_template('admin/dashboard.html',
                           total_treks=total_treks,
                           total_users=total_users,
                           total_staff=total_staff,
                           total_bookings=total_bookings)

@admin_bp.route('/treks', methods=['GET', 'POST'])
@login_required
def manage_treks():
    admin_required()
    form = TrekForm()
    if form.validate_on_submit():
        trek = Trek(
            name=form.name.data,
            location=form.location.data,
            difficulty=form.difficulty.data,
            duration_days=(form.end_date.data - form.start_date.data).days,
            available_slots=form.available_slots.data,
            status=form.status.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            created_by_admin_id=current_user.id
        )
        db.session.add(trek)
        db.session.commit()
        flash('Trek created successfully.', 'success')
        return redirect(url_for('admin.manage_treks'))
    treks = Trek.query.all()
    return render_template('admin/treks.html', form=form, treks=treks)

@admin_bp.route('/trek/edit/<int:trek_id>', methods=['GET', 'POST'])
@login_required
def edit_trek(trek_id):
    admin_required()
    trek = Trek.query.get_or_404(trek_id)
    form = TrekForm(obj=trek)
    if form.validate_on_submit():
        trek.name = form.name.data
        trek.location = form.location.data
        trek.difficulty = form.difficulty.data
        trek.duration_days = (form.end_date.data - form.start_date.data).days
        trek.available_slots = form.available_slots.data
        trek.status = form.status.data
        trek.start_date = form.start_date.data
        trek.end_date = form.end_date.data
        db.session.commit()
        flash('Trek updated successfully.', 'success')
        return redirect(url_for('admin.manage_treks'))
    return render_template('admin/trek_form.html', form=form, trek=trek)

@admin_bp.route('/trek/delete/<int:trek_id>', methods=['POST'])
@login_required
def delete_trek(trek_id):
    admin_required()
    trek = Trek.query.get_or_404(trek_id)
    TrekStaffAssignment.query.filter_by(trek_id=trek.id).delete()
    Booking.query.filter_by(trek_id=trek.id).delete()
    db.session.delete(trek)
    db.session.commit()
    flash('Trek deleted.', 'success')
    return redirect(url_for('admin.manage_treks'))

@admin_bp.route('/staff')
@login_required
def manage_staff():
    admin_required()
    staff_users = User.query.filter_by(role='staff').all()
    return render_template('admin/staff.html', staff_users=staff_users)

@admin_bp.route('/staff/approve/<int:user_id>')
@login_required
def approve_staff(user_id):
    admin_required()
    user = User.query.get_or_404(user_id)
    if user.role != 'staff':
        flash('User is not a staff member.', 'danger')
        return redirect(url_for('admin.manage_staff'))
    profile = user.staff_profile
    if profile:
        profile.approved = True
        db.session.commit()
        flash(f'Staff {user.username} approved.', 'success')
    else:
        flash('Staff profile not found.', 'danger')
    return redirect(url_for('admin.manage_staff'))

@admin_bp.route('/staff/blacklist/<int:user_id>')
@login_required
def blacklist_staff(user_id):
    admin_required()
    user = User.query.get_or_404(user_id)
    if user.role != 'staff':
        flash('User is not a staff member.', 'danger')
        return redirect(url_for('admin.manage_staff'))
    user.is_blacklisted = not user.is_blacklisted
    db.session.commit()
    status = 'blacklisted' if user.is_blacklisted else 'unblacklisted'
    flash(f'Staff {user.username} {status}.', 'success')
    return redirect(url_for('admin.manage_staff'))

@admin_bp.route('/users')
@login_required
def manage_users():
    admin_required()
    users = User.query.filter_by(role='user').all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/user/blacklist/<int:user_id>')
@login_required
def blacklist_user(user_id):
    admin_required()
    user = User.query.get_or_404(user_id)
    if user.role != 'user':
        flash('User is not a trekker.', 'danger')
        return redirect(url_for('admin.manage_users'))
    user.is_blacklisted = not user.is_blacklisted
    db.session.commit()
    status = 'blacklisted' if user.is_blacklisted else 'unblacklisted'
    flash(f'User {user.username} {status}.', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/assign-staff', methods=['GET', 'POST'])
@login_required
def assign_staff():
    admin_required()
    if request.method == 'POST':
        trek_id = request.form.get('trek_id')
        staff_id = request.form.get('staff_id')
        if not trek_id or not staff_id:
            flash('Please select both trek and staff.', 'danger')
            return redirect(url_for('admin.assign_staff'))
        trek = Trek.query.get_or_404(trek_id)
        staff_user = User.query.get_or_404(staff_id)
        if staff_user.role != 'staff' or not staff_user.staff_profile.approved:
            flash('Selected staff is not approved.', 'danger')
            return redirect(url_for('admin.assign_staff'))
        existing = TrekStaffAssignment.query.filter_by(trek_id=trek.id, staff_id=staff_user.staff_profile.id).first()
        if existing:
            flash('This staff is already assigned to the trek.', 'warning')
        else:
            assignment = TrekStaffAssignment(trek_id=trek.id, staff_id=staff_user.staff_profile.id)
            db.session.add(assignment)
            db.session.commit()
            flash('Staff assigned successfully.', 'success')
        return redirect(url_for('admin.assign_staff'))
    treks = Trek.query.all()
    staff_members = User.query.filter_by(role='staff').all()
    approved_staff = [u for u in staff_members if u.staff_profile and u.staff_profile.approved]
    assignments = TrekStaffAssignment.query.all()
    return render_template('admin/assign_staff.html', 
                           treks=treks, 
                           staff_members=approved_staff,
                           assignments=assignments)

@admin_bp.route('/remove-staff/<int:assignment_id>', methods=['POST'])
@login_required
def remove_staff_assignment(assignment_id):
    admin_required()
    assignment = TrekStaffAssignment.query.get_or_404(assignment_id)
    db.session.delete(assignment)
    db.session.commit()
    flash('Staff removed from trek.', 'success')
    return redirect(url_for('admin.assign_staff'))

@admin_bp.route('/bookings')
@login_required
def view_bookings():
    admin_required()
    bookings = Booking.query.all()
    return render_template('admin/bookings.html', bookings=bookings)

@admin_bp.route('/search', methods=['GET'])
@login_required
def search():
    admin_required()
    query = request.args.get('q', '').strip()
    if not query:
        flash('Please enter a search term.', 'warning')
        return redirect(url_for('admin.dashboard'))
    users = User.query.filter(
        (User.username.ilike(f'%{query}%')) | (User.id == query) if query.isdigit() else User.username.ilike(f'%{query}%')
    ).all()
    treks = Trek.query.filter(
        (Trek.name.ilike(f'%{query}%')) | (Trek.id == query) if query.isdigit() else Trek.name.ilike(f'%{query}%')
    ).all()
    return render_template('admin/search_results.html', query=query, users=users, treks=treks)