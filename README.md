# Star Mango Management System

A comprehensive Django-based management system for mango businesses.

## Features

- Inventory Management
- Sales Tracking
- Customer Management
- Purchase Management
- Financial Reports
- PDF Invoice Generation

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/yourusername/StarMango.git
cd StarMango
```

2. Create and activate virtual environment:
```bash
python -m venv djangoenv
.\djangoenv\Scripts\activate  # On Windows
source djangoenv/bin/activate  # On Unix/MacOS
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

7. Access the application:
- Main site: http://127.0.0.1:8000/
- Admin interface: http://127.0.0.1:8000/admin/

## Requirements

- Python 3.8+
- Django 5.0+
- Other dependencies listed in requirements.txt

## License

This project is licensed under the MIT License - see the LICENSE file for details. 