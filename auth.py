from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, StaffProfile
from forms import LoginForm, RegistrationForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already taken.', 'danger')
            return render_template('auth/register.html', form=form)
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html', form=form)
        hashed = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed,
            role=form.role.data
        )
        db.session.add(user)
        db.session.commit()

        if form.role.data == 'staff':
            profile = StaffProfile(user_id=user.id, approved=False)
            db.session.add(profile)
            db.session.commit()
            flash('Staff registration submitted. Await admin approval.', 'info')
        else:
            flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard_redirect'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            if user.is_blacklisted:
                flash('Your account has been blacklisted. Contact admin.', 'danger')
                return redirect(url_for('auth.login'))
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('auth.dashboard_redirect'))
        flash('Invalid username or password.', 'danger')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/dashboard-redirect')
@login_required
def dashboard_redirect():
    if current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif current_user.role == 'staff':
        if current_user.staff_profile and current_user.staff_profile.approved:
            return redirect(url_for('staff.dashboard'))
        else:
            flash('Your staff account is pending admin approval.', 'warning')
            logout_user()
            return redirect(url_for('auth.login'))
    else:
        return redirect(url_for('user.dashboard'))