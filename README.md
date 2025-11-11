# micro-project-fullstack-04
medical record system which ensure the things to be done easier to medical records ,billing, etc 
# Medical Record System

A comprehensive web-based Medical Record System built with Django that helps healthcare providers manage patient records, appointments, and medical reports efficiently.

## Features

- **Patient Management**: Add, view, edit, and manage patient records
- **Appointment Scheduling**: Schedule, reschedule, and track patient appointments
- **Doctor Management**: Manage doctor profiles and availability
- **Medical Records**: Store and access patient medical history and reports
- **User Authentication**: Secure login and role-based access control
- **Responsive Design**: Works on desktop and mobile devices
- **Dark/Light Theme**: User-selectable theme for better accessibility

## Technologies Used

- **Backend**: Django 3.2.1
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: SQLite (development), PostgreSQL (production-ready)
- **Authentication**: Django's built-in authentication system
- **Deployment**: Ready for deployment on Heroku, AWS, or any WSGI-compatible server

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mrs/medical_record_system
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (admin)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Open your browser and go to: http://127.0.0.1:8000/
   - Admin interface: http://127.0.0.1:8000/admin/

## Project Structure

```
medical_record_system/
├── media/                  # User-uploaded files (reports, images)
├── medical_record_system/  # Project settings and configurations
├── records/               # Main application
│   ├── migrations/        # Database migrations
│   ├── static/            # Static files (CSS, JS, images)
│   ├── templates/         # HTML templates
│   ├── __init__.py
│   ├── admin.py          # Admin configurations
│   ├── apps.py           # App configurations
│   ├── forms.py          # Form definitions
│   ├── models.py         # Database models
│   ├── urls.py          # URL configurations
│   └── views.py         # View functions/classes
├── manage.py             # Django's command-line utility
└── requirements.txt      # Project dependencies
```

## Features in Detail

### Patient Management
- Create and manage patient profiles
- Store personal and medical information
- Track patient history and appointments

### Appointment System
- Schedule and manage appointments
- Send notifications for upcoming appointments
- View appointment history

### Medical Records
- Upload and view medical reports
- Maintain treatment history
- Track medications and prescriptions

### User Interface
- Clean, modern interface
- Responsive design for all devices
- Dark/Light theme support

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue in the repository or contact the project maintainers.

---

**Note**: This is a development version. For production use, please ensure proper security measures are in place, including:
- Using a production-ready database (PostgreSQL/MySQL)
- Setting up proper environment variables
- Configuring HTTPS
- Implementing proper user authentication and authorization
4MC23IS077	Preethi K R
4MC23IS089	Roopika H
4MC23IS104	Sinchana B N
4MC24IS407	Pragna H U
4MC24IS410	Spoorthi C P
