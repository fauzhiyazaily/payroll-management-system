from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, send_file
from flask_login import LoginManager, login_required, current_user
from config import Config
from datetime import datetime, date
import pandas as pd
from io import BytesIO
import os

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Flask-Login FIRST
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# Import models after app creation to avoid circular imports
from models import db, User, Employee, PayrollRecord, Attendance, TaxConfiguration

# Initialize database
db.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Import and register auth blueprint
from auth import auth

app.register_blueprint(auth)

# Import PayrollCalculator
try:
    from payroll_calculations import PayrollCalculator
except ImportError:
    print("Warning: Using simplified PayrollCalculator")


    # Simple fallback implementation
    class PayrollCalculator:
        def calculate_payroll(self, employee_id, pay_period_start, pay_period_end, bonus=0, allowances=0):
            employee = Employee.query.get(employee_id)
            if not employee:
                raise ValueError("Employee not found")

            base_salary_period = employee.base_salary / 2
            gross_pay = base_salary_period + bonus + allowances
            tax_deduction = gross_pay * 0.2
            total_deductions = tax_deduction
            net_pay = gross_pay - total_deductions

            payroll_record = PayrollRecord(
                employee_id=employee_id,
                pay_period_start=pay_period_start,
                pay_period_end=pay_period_end,
                pay_date=datetime.now().date(),
                base_salary=base_salary_period,
                gross_pay=gross_pay,
                tax_deduction=tax_deduction,
                total_deductions=total_deductions,
                net_pay=net_pay,
                status='processed'
            )
            return payroll_record

        def generate_payroll_for_all(self, pay_period_start, pay_period_end):
            return []

# Initialize database and create admin user
with app.app_context():
    db.create_all()
    from auth import init_admin_user

    init_admin_user()

    # Initialize tax brackets if not exists
    if not TaxConfiguration.query.first():
        tax_brackets = [
            TaxConfiguration(tax_bracket="10% Bracket", min_income=0, max_income=11000, tax_rate=10),
            TaxConfiguration(tax_bracket="12% Bracket", min_income=11001, max_income=44725, tax_rate=12),
            TaxConfiguration(tax_bracket="22% Bracket", min_income=44726, max_income=95375, tax_rate=22),
            TaxConfiguration(tax_bracket="24% Bracket", min_income=95376, max_income=182100, tax_rate=24),
            TaxConfiguration(tax_bracket="32% Bracket", min_income=182101, max_income=231250, tax_rate=32),
            TaxConfiguration(tax_bracket="35% Bracket", min_income=231251, max_income=578125, tax_rate=35),
            TaxConfiguration(tax_bracket="37% Bracket", min_income=578126, max_income=None, tax_rate=37),
        ]
        db.session.bulk_save_objects(tax_brackets)
        db.session.commit()
        print("Tax brackets initialized")


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth.login'))


@app.route('/dashboard')
@login_required
def dashboard():
    # Dashboard statistics
    total_employees = Employee.query.filter_by(is_active=True).count()
    total_payroll_processed = PayrollRecord.query.filter_by(status='processed').count()

    # Recent payroll records
    recent_payroll = PayrollRecord.query.order_by(PayrollRecord.created_at.desc()).limit(5).all()

    # Department statistics
    departments = db.session.query(
        Employee.department,
        db.func.count(Employee.id).label('count'),
        db.func.avg(Employee.base_salary).label('avg_salary')
    ).filter(Employee.is_active == True).group_by(Employee.department).all()

    return render_template('dashboard.html',
                           total_employees=total_employees,
                           total_payroll_processed=total_payroll_processed,
                           recent_payroll=recent_payroll,
                           departments=departments)


@app.route('/employees')
@login_required
def employees():
    if current_user.role not in ['admin', 'hr']:
        flash('Access denied. HR or Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))

    employees_list = Employee.query.filter_by(is_active=True).all()
    return render_template('employees.html', employees=employees_list)


@app.route('/employees/add', methods=['POST'])
@login_required
def add_employee():
    if current_user.role not in ['admin', 'hr']:
        return jsonify({'error': 'Access denied'}), 403

    try:
        # Create user first
        user = User(
            username=request.form['username'],
            email=request.form['email'],
            role='employee',
            department=request.form['department']
        )
        user.set_password('default123')  # Default password

        db.session.add(user)
        db.session.flush()  # Get user ID

        # Create employee
        employee = Employee(
            user_id=user.id,
            employee_id=request.form['employee_id'],
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            email=request.form['email'],
            phone=request.form['phone'],
            address=request.form['address'],
            department=request.form['department'],
            position=request.form['position'],
            hire_date=datetime.strptime(request.form['hire_date'], '%Y-%m-%d').date(),
            employment_type=request.form['employment_type'],
            base_salary=float(request.form['base_salary']),
            bank_account=request.form['bank_account'],
            tax_id=request.form['tax_id']
        )

        db.session.add(employee)
        db.session.commit()

        flash('Employee added successfully!', 'success')
        return jsonify({'message': 'Employee added successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@app.route('/payroll')
@login_required
def payroll():
    if current_user.role not in ['admin', 'hr']:
        flash('Access denied. HR or Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))

    payroll_records = PayrollRecord.query.order_by(PayrollRecord.created_at.desc()).all()
    employees = Employee.query.filter_by(is_active=True).all()

    return render_template('payroll.html',
                           payroll_records=payroll_records,
                           employees=employees)


@app.route('/payroll/calculate', methods=['POST'])
@login_required
def calculate_payroll():
    if current_user.role not in ['admin', 'hr']:
        return jsonify({'error': 'Access denied'}), 403

    try:
        calculator = PayrollCalculator()
        employee_id = int(request.form['employee_id'])
        pay_period_start = datetime.strptime(request.form['pay_period_start'], '%Y-%m-%d').date()
        pay_period_end = datetime.strptime(request.form['pay_period_end'], '%Y-%m-%d').date()
        bonus = float(request.form.get('bonus', 0))
        allowances = float(request.form.get('allowances', 0))

        payroll_record = calculator.calculate_payroll(
            employee_id, pay_period_start, pay_period_end, bonus, allowances
        )

        db.session.add(payroll_record)
        db.session.commit()

        return jsonify({
            'message': 'Payroll calculated successfully',
            'payroll_id': payroll_record.id
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/payroll/generate_all', methods=['POST'])
@login_required
def generate_all_payroll():
    if current_user.role not in ['admin']:
        return jsonify({'error': 'Admin access required'}), 403

    try:
        calculator = PayrollCalculator()
        pay_period_start = datetime.strptime(request.form['pay_period_start'], '%Y-%m-%d').date()
        pay_period_end = datetime.strptime(request.form['pay_period_end'], '%Y-%m-%d').date()

        payroll_records = calculator.generate_payroll_for_all(pay_period_start, pay_period_end)

        db.session.bulk_save_objects(payroll_records)
        db.session.commit()

        return jsonify({
            'message': f'Payroll generated for {len(payroll_records)} employees',
            'count': len(payroll_records)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/reports')
@login_required
def reports():
    if current_user.role not in ['admin', 'hr']:
        flash('Access denied. HR or Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))

    return render_template('reports.html')


@app.route('/reports/generate', methods=['POST'])
@login_required
def generate_report():
    if current_user.role not in ['admin', 'hr']:
        return jsonify({'error': 'Access denied'}), 403

    try:
        report_type = request.form['report_type']
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()

        if report_type == 'payroll_summary':
            records = PayrollRecord.query.filter(
                PayrollRecord.pay_period_start >= start_date,
                PayrollRecord.pay_period_end <= end_date
            ).all()

            data = []
            for record in records:
                data.append({
                    'Employee': f"{record.employee.first_name} {record.employee.last_name}",
                    'Pay Period': f"{record.pay_period_start} to {record.pay_period_end}",
                    'Gross Pay': record.gross_pay,
                    'Deductions': record.total_deductions,
                    'Net Pay': record.net_pay,
                    'Status': record.status
                })

            df = pd.DataFrame(data)
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Payroll Summary', index=False)
            output.seek(0)

            return send_file(output,
                             download_name=f'payroll_summary_{start_date}_{end_date}.xlsx',
                             as_attachment=True)

        elif report_type == 'employee_list':
            employees = Employee.query.filter_by(is_active=True).all()

            data = []
            for emp in employees:
                data.append({
                    'Employee ID': emp.employee_id,
                    'First Name': emp.first_name,
                    'Last Name': emp.last_name,
                    'Department': emp.department,
                    'Position': emp.position,
                    'Base Salary': emp.base_salary,
                    'Hire Date': emp.hire_date
                })

            df = pd.DataFrame(data)
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Employee List', index=False)
            output.seek(0)

            return send_file(output,
                             download_name=f'employee_list_{date.today()}.xlsx',
                             as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/profile')
@login_required
def profile():
    employee = Employee.query.filter_by(user_id=current_user.id).first()
    payroll_history = PayrollRecord.query.filter_by(employee_id=employee.id).order_by(
        PayrollRecord.created_at.desc()
    ).limit(10).all() if employee else []

    return render_template('profile.html',
                           employee=employee,
                           payroll_history=payroll_history)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)