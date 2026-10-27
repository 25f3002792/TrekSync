# TrekSync

A web application built with Flask for managing trekking expeditions, slot reservations, and guide coordination.

TrekSync provides a centralized platform for adventure travel operators to manage trek itineraries, assign field guides, prevent overbooking with live slot counts, and manage trekker reservations.

---

## Features

### Trekker (User)
- Browse open treks with search and filtering by difficulty (`Easy`, `Moderate`, `Hard`) and location.
- Book available trek slots with duplicate-booking prevention.
- View booking history and reservation status.
- Cancel bookings with automatic slot replenishment.
- Edit user profile.

### Trek Staff / Guide
- Register as staff (requires admin approval before access).
- Dashboard showing assigned treks.
- View participant manifests for assigned treks.
- Update live trek status (`Open`, `Closed`, `Completed`) and remaining slots.

### Admin
- Dashboard with platform stats (treks, users, staff, bookings).
- Trek management (CRUD operations with start/end date validation).
- Review and approve or blacklist staff registrations.
- Assign approved staff to specific treks.
- User management and account blacklisting.
- Global search across users and treks.
- View all bookings across the platform.

### REST API
- `GET /api/treks`: List all treks (public).
- `GET /api/bookings`: View bookings (session-authenticated; admins see all, users see their own).
- OpenAPI 3.0 specification provided in `api.yaml`.

---

## Tech Stack

- **Backend:** Python 3, Flask
- **Database & ORM:** SQLite, Flask-SQLAlchemy
- **Authentication & Security:** Flask-Login, Werkzeug (password hashing), Flask-WTF (CSRF protection)
- **Frontend:** Jinja2 templates, Bootstrap 5, FontAwesome
- **API Spec:** OpenAPI 3.0 (`api.yaml`)

---

## Project Structure

```text
TrekSync/
├── app.py              # Application entry point & blueprint registration
├── config.py           # Configuration settings
├── models.py           # Database models (User, StaffProfile, Trek, Booking, TrekStaffAssignment)
├── forms.py            # WTForms validation classes
├── requirements.txt    # Project dependencies
├── api.py              # REST API blueprint (/api)
├── api.yaml            # OpenAPI 3.0 specification
├── auth.py             # Authentication routes (login, register, logout)
├── admin.py            # Admin dashboard and management routes
├── staff.py            # Staff dashboard and trek management routes
├── user.py             # Trekker dashboard, browsing, and booking routes
└── templates/          # HTML templates (Jinja2 + Bootstrap)
    ├── base.html
    ├── auth/
    ├── admin/
    ├── staff/
    └── user/
```

---

## Getting Started

### 1. Prerequisites
- Python 3.10+
- Git

### 2. Clone the Repository
```bash
git clone https://github.com/25f3002792/TrekSync.git
cd TrekSync
```

### 3. Create a Virtual Environment

- **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```

- **Windows (Command Prompt):**
  ```cmd
  python -m venv venv
  .\venv\Scripts\activate.bat
  ```

- **macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Application
```bash
python app.py
```

The database tables and a default admin user are created automatically on the first run.
Open your browser and navigate to: **`http://127.0.0.1:5000`**

---

## Default Credentials

| Role | Username | Password | Notes |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | Pre-created automatically on first launch |
| **Staff** | *Register via UI* | *Your choice* | Requires admin approval in `/admin/staff` |
| **User** | *Register via UI* | *Your choice* | Immediate access upon registration |

---

## Key Workflows to Test

1. **User Booking Flow:** Register as a trekker → browse treks → book an open trek (slots decrement by 1) → check bookings page → cancel booking (slot restored).
2. **Staff Approval Flow:** Register as staff → try logging in (blocked pending approval) → log in as `admin` → approve staff in `/admin/staff` → assign staff to a trek in `/admin/assign-staff` → log in as staff to view assigned treks and participant list.
3. **Date Validation:** Try creating a trek with an end date earlier than the start date or in the past to verify form validation.
4. **Blacklist Flow:** Admin blacklists a user/staff member → that user is prevented from logging in.
