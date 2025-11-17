from datetime import datetime, timedelta
from models import db, Employee, PayrollRecord, TaxConfiguration, Attendance


class PayrollCalculator:
    def __init__(self):
        self.OVERTIME_RATE = 1.5
        self.SOCIAL_SECURITY_RATE = 0.062
        self.MEDICARE_RATE = 0.0145
        self.STANDARD_WORK_HOURS = 40

    def calculate_tax(self, gross_income):
        """Calculate tax based on progressive tax brackets"""
        tax_configs = TaxConfiguration.query.filter_by(is_active=True).order_by(TaxConfiguration.min_income).all()
        tax_amount = 0
        remaining_income = gross_income

        for bracket in tax_configs:
            if remaining_income <= 0:
                break

            if bracket.max_income is None or gross_income <= bracket.max_income:
                taxable_in_bracket = min(remaining_income,
                                         (
                                                     bracket.max_income - bracket.min_income) if bracket.max_income else remaining_income)
            else:
                taxable_in_bracket = bracket.max_income - bracket.min_income

            tax_amount += taxable_in_bracket * (bracket.tax_rate / 100)
            remaining_income -= taxable_in_bracket

        return round(tax_amount, 2)

    def calculate_overtime_pay(self, base_salary, overtime_hours):
        """Calculate overtime pay (1.5x hourly rate)"""
        hourly_rate = base_salary / (4 * self.STANDARD_WORK_HOURS)  # Monthly salary to hourly
        overtime_pay = overtime_hours * hourly_rate * self.OVERTIME_RATE
        return round(overtime_pay, 2)

    def calculate_social_security(self, gross_pay):
        """Calculate social security deduction"""
        return round(gross_pay * self.SOCIAL_SECURITY_RATE, 2)

    def calculate_health_insurance(self, gross_pay):
        """Calculate health insurance deduction"""
        return round(gross_pay * self.MEDICARE_RATE, 2)

    def calculate_payroll(self, employee_id, pay_period_start, pay_period_end, bonus=0, allowances=0):
        """Calculate complete payroll for an employee"""
        employee = Employee.query.get(employee_id)
        if not employee:
            raise ValueError("Employee not found")

        # Calculate overtime from attendance records
        attendance_records = Attendance.query.filter(
            Attendance.employee_id == employee_id,
            Attendance.date >= pay_period_start,
            Attendance.date <= pay_period_end
        ).all()

        total_overtime = sum(record.overtime_hours for record in attendance_records)

        # Calculate base pay for the period (assuming semi-monthly payroll)
        base_salary_period = employee.base_salary / 2

        # Calculate overtime pay
        overtime_pay = self.calculate_overtime_pay(employee.base_salary, total_overtime)

        # Calculate gross pay
        gross_pay = base_salary_period + overtime_pay + bonus + allowances

        # Calculate deductions
        tax_deduction = self.calculate_tax(gross_pay)
        social_security = self.calculate_social_security(gross_pay)
        health_insurance = self.calculate_health_insurance(gross_pay)
        total_deductions = tax_deduction + social_security + health_insurance

        # Calculate net pay
        net_pay = gross_pay - total_deductions

        # Create payroll record
        payroll_record = PayrollRecord(
            employee_id=employee_id,
            pay_period_start=pay_period_start,
            pay_period_end=pay_period_end,
            pay_date=datetime.now().date(),
            base_salary=base_salary_period,
            overtime_hours=total_overtime,
            overtime_pay=overtime_pay,
            bonus=bonus,
            allowances=allowances,
            gross_pay=gross_pay,
            tax_deduction=tax_deduction,
            social_security=social_security,
            health_insurance=health_insurance,
            total_deductions=total_deductions,
            net_pay=net_pay,
            status='processed'
        )

        return payroll_record

    def generate_payroll_for_all(self, pay_period_start, pay_period_end):
        """Generate payroll for all active employees"""
        active_employees = Employee.query.filter_by(is_active=True).all()
        payroll_records = []

        for employee in active_employees:
            try:
                payroll_record = self.calculate_payroll(
                    employee.id,
                    pay_period_start,
                    pay_period_end
                )
                payroll_records.append(payroll_record)
            except Exception as e:
                print(f"Error processing payroll for {employee.first_name} {employee.last_name}: {str(e)}")
                continue

        return payroll_records