// Reports and analytics functionality
const reportsManager = {
    // Initialize reports page
    init: () => {
        // Initialize date range picker
        const dateRangeForm = document.getElementById('dateRangeForm');
        if (dateRangeForm) {
            dateRangeForm.addEventListener('submit', reportsManager.handleDateRangeChange);
        }

        // Initialize charts
        reportsManager.initCharts();

        // Initialize export buttons
        reportsManager.initExportButtons();
    },

    // Handle date range change
    handleDateRangeChange: async (e) => {
        e.preventDefault();
        utils.showLoading();

        try {
            const formData = new FormData(e.target);
            const response = await fetch(e.target.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            });

            if (response.ok) {
                const data = await response.json();
                reportsManager.updateCharts(data);
            } else {
                utils.showAlert('Error updating reports', 'danger');
            }
        } catch (error) {
            utils.showAlert('Error updating reports', 'danger');
        } finally {
            utils.hideLoading();
        }
    },

    // Initialize charts
    initCharts: () => {
        // Sales trend chart
        const salesTrendCtx = document.getElementById('salesTrendChart');
        if (salesTrendCtx) {
            new Chart(salesTrendCtx, {
                type: 'line',
                data: {
                    labels: salesTrendData.labels,
                    datasets: [{
                        label: 'Sales',
                        data: salesTrendData.data,
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }]
                },
                options: chartConfig.lineChartOptions
            });
        }

        // Inventory status chart
        const inventoryStatusCtx = document.getElementById('inventoryStatusChart');
        if (inventoryStatusCtx) {
            new Chart(inventoryStatusCtx, {
                type: 'doughnut',
                data: {
                    labels: inventoryStatusData.labels,
                    datasets: [{
                        data: inventoryStatusData.data,
                        backgroundColor: [
                            'rgb(75, 192, 192)',
                            'rgb(255, 205, 86)',
                            'rgb(255, 99, 132)'
                        ]
                    }]
                },
                options: chartConfig.doughnutChartOptions
            });
        }

        // Payment methods chart
        const paymentMethodsCtx = document.getElementById('paymentMethodsChart');
        if (paymentMethodsCtx) {
            new Chart(paymentMethodsCtx, {
                type: 'pie',
                data: {
                    labels: paymentMethodsData.labels,
                    datasets: [{
                        data: paymentMethodsData.data,
                        backgroundColor: [
                            'rgb(75, 192, 192)',
                            'rgb(255, 205, 86)',
                            'rgb(255, 99, 132)',
                            'rgb(54, 162, 235)'
                        ]
                    }]
                },
                options: chartConfig.pieChartOptions
            });
        }
    },

    // Update charts with new data
    updateCharts: (data) => {
        // Update sales trend chart
        const salesTrendChart = Chart.getChart('salesTrendChart');
        if (salesTrendChart) {
            salesTrendChart.data.labels = data.sales_trend.labels;
            salesTrendChart.data.datasets[0].data = data.sales_trend.data;
            salesTrendChart.update();
        }

        // Update inventory status chart
        const inventoryStatusChart = Chart.getChart('inventoryStatusChart');
        if (inventoryStatusChart) {
            inventoryStatusChart.data.labels = data.inventory_status.labels;
            inventoryStatusChart.data.datasets[0].data = data.inventory_status.data;
            inventoryStatusChart.update();
        }

        // Update payment methods chart
        const paymentMethodsChart = Chart.getChart('paymentMethodsChart');
        if (paymentMethodsChart) {
            paymentMethodsChart.data.labels = data.payment_methods.labels;
            paymentMethodsChart.data.datasets[0].data = data.payment_methods.data;
            paymentMethodsChart.update();
        }

        // Update summary cards
        document.getElementById('totalSales').textContent = utils.formatCurrency(data.total_sales);
        document.getElementById('totalPurchases').textContent = utils.formatCurrency(data.total_purchases);
        document.getElementById('netProfit').textContent = utils.formatCurrency(data.net_profit);
        document.getElementById('averageOrderValue').textContent = utils.formatCurrency(data.average_order_value);
    },

    // Initialize export buttons
    initExportButtons: () => {
        // Export sales report
        const exportSalesBtn = document.getElementById('exportSalesReport');
        if (exportSalesBtn) {
            exportSalesBtn.addEventListener('click', () => reportsManager.exportReport('sales'));
        }

        // Export inventory report
        const exportInventoryBtn = document.getElementById('exportInventoryReport');
        if (exportInventoryBtn) {
            exportInventoryBtn.addEventListener('click', () => reportsManager.exportReport('inventory'));
        }

        // Export financial report
        const exportFinancialBtn = document.getElementById('exportFinancialReport');
        if (exportFinancialBtn) {
            exportFinancialBtn.addEventListener('click', () => reportsManager.exportReport('financial'));
        }

        // Export chart images
        document.querySelectorAll('.export-chart').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const chartId = e.target.dataset.chartId;
                reportsManager.exportChartImage(chartId);
            });
        });
    },

    // Export report
    exportReport: async (type) => {
        utils.showLoading();

        try {
            const response = await fetch(`/reports/export/${type}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${type}_report.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            } else {
                utils.showAlert('Error exporting report', 'danger');
            }
        } catch (error) {
            utils.showAlert('Error exporting report', 'danger');
        } finally {
            utils.hideLoading();
        }
    },

    // Export chart as image
    exportChartImage: (chartId) => {
        const canvas = document.getElementById(chartId);
        if (!canvas) return;

        const link = document.createElement('a');
        link.download = `${chartId}.png`;
        link.href = canvas.toDataURL('image/png');
        link.click();
    }
};

// Initialize reports functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    reportsManager.init();
}); 