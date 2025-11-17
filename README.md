#  Employee Payroll Management System

A comprehensive web-based payroll management system built with Python Flask, featuring real-time payroll calculations, multi-level user access, and an impressive modern UI.

##  Features

###  Payroll Management
- Automated payroll calculations with progressive tax brackets
- Overtime pay computation (1.5x hourly rate)
- Social security and medicare deductions
- Bonus and allowance management

###  Employee Management
- Complete employee database with personal and salary information
- Department and position management
- Employment type tracking (full-time, part-time, contract)

###  Security & Access Control
- Multi-level role-based access (Admin, HR, Employee)
- Secure password hashing with Werkzeug
- Session management with Flask-Login
- Protected routes and data access

###  Reporting & Analytics
- Excel report generation for payroll and employee data
- Interactive charts and dashboard analytics
- Department-wise salary comparisons
- Payroll trend analysis

###  Modern UI/UX
- Responsive design with gradient backgrounds
- Interactive charts using Chart.js
- Professional card-based layout
- Mobile-friendly interface

## Technology Stack

### Backend
- **Python Flask** - Web framework
- **SQLAlchemy** - ORM for database operations
- **Flask-Login** - User session management
- **Pandas** - Data processing and Excel reports

### Frontend
- **HTML5/CSS3** - Modern responsive design
- **JavaScript** - Interactive UI components
- **Chart.js** - Data visualization
- **Bootstrap 5** - UI framework
- **Font Awesome** - Icons

### Database
- **SQLite** (Development) / **PostgreSQL** (Production ready)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/payroll-management-system.git
   cd payroll-management-system
2. Create virtual environment
'''bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
3.Install dependencies
'''bash
pip install -r requirements.txt
4.Run the application
'''bash
python app.py
5.Access the application
Open http://localhost:5000 in your browser
