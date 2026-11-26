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

## Core feature: Laundry Order Management
Customers book laundry pickups and track their orders; admins manage services and order status.

**Customer**
- Browse available services and place an order (service, estimated weight, pickup address and date, notes)
- The total price is computed automatically (weight x price per kg)
- View, edit (pending only), cancel, and delete their own orders
- Dashboard shows active, completed, and recent orders

**Admin**
- Create, edit, and delete services (a service with orders can only be marked unavailable)
- View all orders, filter by status, and update status (Pending, Washing, Ready, Completed, Cancelled)
- Dashboard shows total orders, pending orders, completed revenue, and recent orders

**Validation and rules**
- Weight must be 1 to 50 kg; pickup date cannot be in the past; address is required
- Completed or cancelled orders cannot be changed
- Customers can only open their own orders; other users get a 404
- Only logged-in users can access the feature; role-based pages redirect other roles

**Database relationships**
- User (1) to (many) Order
- Service (1) to (many) Order

## Test accounts
- Admin: see the completion report
- Customer: register through the registration form
