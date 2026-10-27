from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')
    is_blacklisted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    staff_profile = db.relationship('StaffProfile', backref='user', uselist=False)
    bookings = db.relationship('Booking', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'

class StaffProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    contact_phone = db.Column(db.String(20))
    approved = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='Active')

    trek_assignments = db.relationship('TrekStaffAssignment', backref='staff', lazy=True)

    def __repr__(self):
        return f'<StaffProfile {self.user.username}>'

class Trek(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    difficulty = db.Column(db.String(20), default='Easy')
    duration_days = db.Column(db.Integer)
    available_slots = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='Pending')
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    created_by_admin_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    bookings = db.relationship('Booking', backref='trek', lazy=True)
    staff_assignments = db.relationship('TrekStaffAssignment', backref='trek', lazy=True)

    def __repr__(self):
        return f'<Trek {self.name} ({self.status})>'

class TrekStaffAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trek_id = db.Column(db.Integer, db.ForeignKey('trek.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff_profile.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('trek_id', 'staff_id', name='unique_trek_staff'),)

    def __repr__(self):
        return f'<TrekStaffAssignment trek={self.trek_id} staff={self.staff_id}>'

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('trek.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    status = db.Column(db.String(20), default='Booked')

    __table_args__ = (db.UniqueConstraint('user_id', 'trek_id', name='unique_user_trek_booking'),)

    def __repr__(self):
        return f'<Booking {self.id} - {self.user.username} -> {self.trek.name} ({self.status})>'