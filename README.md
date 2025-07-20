# College Transport System

A premium, modern web application for managing college transportation, built with Django and Tailwind CSS.

## Features
- Student, Driver, and Admin panels with role-based dashboards
- Book seats, view bus routes, and booking history (students)
- Manage buses, routes, drivers, leave requests, and service logs (admin)
- Apply for leave and view assignments (drivers)
- Custom authentication with premium UI
- Responsive, animated, and glassmorphic design using Tailwind CSS

## Setup Instructions
1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd <project-directory>
   ```
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```
5. **Create a superuser (admin):**
   ```bash
   python manage.py createsuperuser
   ```
6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
7. **Access the app:**
   - Home: http://localhost:8000/
   - Admin Panel: http://localhost:8000/admin/login/
   - Student/Driver: Register and login from the home page

## Tech Stack
- Django (Python)
- Tailwind CSS
- HTML5/CSS3

## License
MIT 