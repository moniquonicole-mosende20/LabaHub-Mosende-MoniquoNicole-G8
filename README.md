# LabaHub

Laundry shop management system built with Django and PostgreSQL (Supabase).
Phase 1 implements the Account Feature.

## Features
- Registration with validation (required fields, valid and unique email, password confirmation)
- Login / logout with error messages
- Role-based dashboards (Admin and Customer); users cannot open another role's dashboard
- User profile view and edit (name, email, contact number, profile photo)

## Tech stack
Django (templates), PostgreSQL via Supabase, Bootstrap 5

## Setup
1. Clone the repository and open the folder.
2. Create and activate a virtual environment:
   ```
   py -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   python -m pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your Supabase (Session pooler) credentials.
5. Run migrations and create an admin:
   ```
   python manage.py migrate
   python manage.py createsuperuser
   ```
6. Start the server:
   ```
   python manage.py runserver
   ```

## Roles
- **Customer**: created through the registration form.
- **Admin**: created with `createsuperuser` or by changing a user's role in the Django admin.
