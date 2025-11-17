// Payroll calculation utilities
class PayrollCalculatorUI {
    constructor() {
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Employee selection
        const employeeSelect = document.getElementById('employeeSelect');
        if (employeeSelect) {
            employeeSelect.addEventListener('change', this.onEmployeeChange.bind(this));
        }

        // Calculate button
        const calculateBtn = document.getElementById('calculatePayroll');
        if (calculateBtn) {
            calculateBtn.addEventListener('click', this.calculatePayroll.bind(this));
        }

        // Generate all button
        const generateAllBtn = document.getElementById('generateAllPayroll');
        if (generateAllBtn) {
            generateAllBtn.addEventListener('click', this.generateAllPayroll.bind(this));
        }
    }

    onEmployeeChange(event) {
        const employeeId = event.target.value;
        if (employeeId) {
            this.loadEmployeeDetails(employeeId);
        }
    }

    async loadEmployeeDetails(employeeId) {
        try {
            // In a real application, you would fetch this from the server
            const response = await fetch(`/api/employees/${employeeId}`);
            const employee = await response.json();

            this.updateEmployeeDisplay(employee);
        } catch (error) {
            console.error('Error loading employee details:', error);
        }
    }

    updateEmployeeDisplay(employee) {
        const displayElement = document.getElementById('employeeDetails');
        if (displayElement && employee) {
            displayElement.innerHTML = `
                <div class="employee-info">
                    <h4>${employee.first_name} ${employee.last_name}</h4>
                    <p><strong>Department:</strong> ${employee.department}</p>
                    <p><strong>Position:</strong> ${employee.position}</p>
                    <p><strong>Base Salary:</strong> $${employee.base_salary.toLocaleString()}</p>
                </div>
            `;
        }
    }

    async calculatePayroll() {
        const form = document.getElementById('payrollCalculationForm');
        if (!form) return;

        const formData = new FormData(form);

        try {
            const response = await fetch('/payroll/calculate', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                showAlert(result.message, 'success');
                // Refresh the page to show new payroll record
                setTimeout(() => location.reload(), 1500);
            } else {
                showAlert(result.error, 'error');
            }
        } catch (error) {
            showAlert('Error calculating payroll. Please try again.', 'error');
        }
    }

    async generateAllPayroll() {
        const form = document.getElementById('bulkPayrollForm');
        if (!form) return;

        if (!confirm('Are you sure you want to generate payroll for all active employees?')) {
            return;
        }

        const formData = new FormData(form);

        try {
            const response = await fetch('/payroll/generate_all', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                showAlert(result.message, 'success');
                setTimeout(() => location.reload(), 1500);
            } else {
                showAlert(result.error, 'error');
            }
        } catch (error) {
            showAlert('Error generating payroll. Please try again.', 'error');
        }
    }

    // Preview payroll calculation
    previewCalculation(baseSalary, overtimeHours, bonus, allowances) {
        const hourlyRate = baseSalary / (4 * 40); // Monthly to hourly
        const overtimePay = overtimeHours * hourlyRate * 1.5;
        const grossPay = (baseSalary / 2) + overtimePay + bonus + allowances;

        // Simplified tax calculation for preview
        const tax = grossPay * 0.2; // 20% estimated
        const socialSecurity = grossPay * 0.062;
        const medicare = grossPay * 0.0145;
        const totalDeductions = tax + socialSecurity + medicare;
        const netPay = grossPay - totalDeductions;

        return {
            grossPay: Math.round(grossPay * 100) / 100,
            deductions: Math.round(totalDeductions * 100) / 100,
            netPay: Math.round(netPay * 100) / 100
        };
    }
}

// Initialize payroll calculator when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PayrollCalculatorUI();
});