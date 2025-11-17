// Chart.js configurations
let payrollChart, departmentChart;

function initializeCharts() {
    // Payroll Summary Chart
    const payrollCtx = document.getElementById('payrollChart');
    if (payrollCtx) {
        payrollChart = new Chart(payrollCtx, {
            type: 'bar',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Gross Pay',
                    data: [120000, 125000, 118000, 132000, 128000, 135000],
                    backgroundColor: '#4361ee',
                    borderColor: '#3a56d4',
                    borderWidth: 1
                }, {
                    label: 'Net Pay',
                    data: [98000, 102000, 96000, 108000, 104000, 110000],
                    backgroundColor: '#4cc9f0',
                    borderColor: '#4895ef',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Payroll Summary (Last 6 Months)'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }

    // Department Distribution Chart
    const departmentCtx = document.getElementById('departmentChart');
    if (departmentCtx) {
        departmentChart = new Chart(departmentCtx, {
            type: 'doughnut',
            data: {
                labels: ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'Operations'],
                datasets: [{
                    data: [30, 20, 15, 10, 12, 13],
                    backgroundColor: [
                        '#4361ee',
                        '#4cc9f0',
                        '#7209b7',
                        '#f72585',
                        '#4895ef',
                        '#3a0ca3'
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'Employee Distribution by Department'
                    }
                }
            }
        });
    }
}

// Update charts with real data
function updatePayrollChart(labels, grossData, netData) {
    if (payrollChart) {
        payrollChart.data.labels = labels;
        payrollChart.data.datasets[0].data = grossData;
        payrollChart.data.datasets[1].data = netData;
        payrollChart.update();
    }
}

function updateDepartmentChart(labels, data) {
    if (departmentChart) {
        departmentChart.data.labels = labels;
        departmentChart.data.datasets[0].data = data;
        departmentChart.update();
    }
}

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeCharts);