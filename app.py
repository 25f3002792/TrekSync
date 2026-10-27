from flask import Flask, redirect, url_for
from config import Config
from models import db, User, Trek
from auth import auth_bp
from admin import admin_bp
from staff import staff_bp
from user import user_bp
from api_routes import api_bp
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from datetime import date, timedelta

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(staff_bp, url_prefix='/staff')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(api_bp)

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

def init_database():
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print('✅ Admin user created: username=admin, password=admin123')

        if Trek.query.count() == 0 and admin:
            sample_treks = [
                Trek(
                    name="Everest Base Camp Trek",
                    location="Khumbu, Nepal",
                    difficulty="Hard",
                    duration_days=14,
                    available_slots=12,
                    status="Open",
                    start_date=date.today() + timedelta(days=15),
                    end_date=date.today() + timedelta(days=29),
                    created_by_admin_id=admin.id
                ),
                Trek(
                    name="Annapurna Circuit",
                    location="Gandaki, Nepal",
                    difficulty="Moderate",
                    duration_days=10,
                    available_slots=18,
                    status="Open",
                    start_date=date.today() + timedelta(days=20),
                    end_date=date.today() + timedelta(days=30),
                    created_by_admin_id=admin.id
                ),
                Trek(
                    name="Kedarkantha Winter Trek",
                    location="Uttarakhand, India",
                    difficulty="Easy",
                    duration_days=6,
                    available_slots=20,
                    status="Open",
                    start_date=date.today() + timedelta(days=10),
                    end_date=date.today() + timedelta(days=16),
                    created_by_admin_id=admin.id
                )
            ]
            db.session.add_all(sample_treks)
            db.session.commit()
            print('✅ Sample treks seeded')

try:
    init_database()
except Exception as e:
    print(f"Database initialization error: {e}")

if __name__ == '__main__':
    app.run(debug=True)