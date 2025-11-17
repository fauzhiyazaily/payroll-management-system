from app import app, db
from models import User, Employee, PayrollRecord, TaxConfiguration, Attendance
from auth import init_admin_user
from datetime import datetime


def create_database():
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully!")

        # Initialize admin user
        init_admin_user()
        print("✅ Admin user created!")

        # Add sample tax brackets
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
            print("✅ Tax brackets added!")

        # Add a sample employee for testing
        if not Employee.query.first():
            # Create a sample user
            sample_user = User(
                username="john_doe",
                email="john@company.com",
                role="employee",
                department="Engineering"
            )
            sample_user.set_password("password123")
            db.session.add(sample_user)
            db.session.flush()

            # Create sample employee
            sample_employee = Employee(
                user_id=sample_user.id,
                employee_id="EMP001",
                first_name="John",
                last_name="Doe",
                email="john@company.com",
                phone="123-456-7890",
                department="Engineering",
                position="Software Engineer",
                hire_date=datetime.now().date(),
                employment_type="full-time",
                base_salary=75000.00,
                bank_account="123456789",
                tax_id="TAX123456"
            )
            db.session.add(sample_employee)
            db.session.commit()
            print("Sample employee added!")

        print(" Database setup completed successfully!")
        print(" Database file should be created at: payroll.db")


if __name__ == '__main__':
    create_database()