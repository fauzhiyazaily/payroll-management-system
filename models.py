from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False, default='employee')  # admin, hr, employee
    department = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship with Employee
    employee = db.relationship('Employee', backref='user', uselist=False, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    department = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    hire_date = db.Column(db.Date, nullable=False)
    employment_type = db.Column(db.String(20), default='full-time')  # full-time, part-time, contract
    base_salary = db.Column(db.Float, nullable=False)
    bank_account = db.Column(db.String(50))
    tax_id = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    payroll_records = db.relationship('PayrollRecord', backref='employee', lazy=True)
    attendance_records = db.relationship('Attendance', backref='employee', lazy=True)


class PayrollRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    pay_period_start = db.Column(db.Date, nullable=False)
    pay_period_end = db.Column(db.Date, nullable=False)
    pay_date = db.Column(db.Date, nullable=False)

    # Earnings
    base_salary = db.Column(db.Float, nullable=False)
    overtime_hours = db.Column(db.Float, default=0)
    overtime_pay = db.Column(db.Float, default=0)
    bonus = db.Column(db.Float, default=0)
    allowances = db.Column(db.Float, default=0)
    gross_pay = db.Column(db.Float, nullable=False)

    # Deductions
    tax_deduction = db.Column(db.Float, default=0)
    social_security = db.Column(db.Float, default=0)
    health_insurance = db.Column(db.Float, default=0)
    other_deductions = db.Column(db.Float, default=0)
    total_deductions = db.Column(db.Float, nullable=False)

    # Final
    net_pay = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, processed, paid
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    check_in = db.Column(db.Time)
    check_out = db.Column(db.Time)
    hours_worked = db.Column(db.Float, default=0)
    overtime_hours = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='present')  # present, absent, late, half-day
    notes = db.Column(db.Text)


class TaxConfiguration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tax_bracket = db.Column(db.String(50), nullable=False)
    min_income = db.Column(db.Float, nullable=False)
    max_income = db.Column(db.Float)
    tax_rate = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True)