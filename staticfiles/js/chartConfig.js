// Chart configuration settings
const chartConfig = {
    // Common chart options
    commonOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    padding: 20,
                    usePointStyle: true
                }
            },
            tooltip: {
                mode: 'index',
                intersect: false,
                padding: 10,
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                titleColor: '#fff',
                bodyColor: '#fff',
                borderColor: 'rgba(255, 255, 255, 0.1)',
                borderWidth: 1,
                displayColors: true,
                callbacks: {
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (context.parsed.y !== null) {
                            label += utils.formatCurrency(context.parsed.y);
                        }
                        return label;
                    }
                }
            }
        }
    },

    // Line chart options
    lineChartOptions: {
        ...chartConfig.commonOptions,
        scales: {
            x: {
                grid: {
                    display: false
                },
                ticks: {
                    maxRotation: 45,
                    minRotation: 45
                }
            },
            y: {
                beginAtZero: true,
                ticks: {
                    callback: function(value) {
                        return utils.formatCurrency(value);
                    }
                }
            }
        }
    },

    // Bar chart options
    barChartOptions: {
        ...chartConfig.commonOptions,
        scales: {
            x: {
                grid: {
                    display: false
                },
                ticks: {
                    maxRotation: 45,
                    minRotation: 45
                }
            },
            y: {
                beginAtZero: true,
                ticks: {
                    callback: function(value) {
                        return utils.formatCurrency(value);
                    }
                }
            }
        }
    },

    // Doughnut chart options
    doughnutChartOptions: {
        ...chartConfig.commonOptions,
        cutout: '60%',
        plugins: {
            ...chartConfig.commonOptions.plugins,
            tooltip: {
                ...chartConfig.commonOptions.plugins.tooltip,
                callbacks: {
                    label: function(context) {
                        const value = context.raw;
                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                        const percentage = ((value / total) * 100).toFixed(1);
                        return `${context.label}: ${value} (${percentage}%)`;
                    }
                }
            }
        }
    },

    // Pie chart options
    pieChartOptions: {
        ...chartConfig.commonOptions,
        plugins: {
            ...chartConfig.commonOptions.plugins,
            tooltip: {
                ...chartConfig.commonOptions.plugins.tooltip,
                callbacks: {
                    label: function(context) {
                        const value = context.raw;
                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                        const percentage = ((value / total) * 100).toFixed(1);
                        return `${context.label}: ${value} (${percentage}%)`;
                    }
                }
            }
        }
    },

    // Chart colors
    colors: {
        primary: 'rgb(75, 192, 192)',
        secondary: 'rgb(255, 205, 86)',
        success: 'rgb(75, 192, 192)',
        danger: 'rgb(255, 99, 132)',
        warning: 'rgb(255, 205, 86)',
        info: 'rgb(54, 162, 235)',
        light: 'rgb(201, 203, 207)',
        dark: 'rgb(36, 36, 36)'
    },

    // Chart datasets
    datasets: {
        // Sales trend dataset
        salesTrend: {
            label: 'Sales',
            borderColor: chartConfig.colors.primary,
            backgroundColor: chartConfig.colors.primary,
            tension: 0.1,
            fill: false
        },

        // Inventory status dataset
        inventoryStatus: {
            backgroundColor: [
                chartConfig.colors.success,
                chartConfig.colors.warning,
                chartConfig.colors.danger
            ]
        },

        // Payment methods dataset
        paymentMethods: {
            backgroundColor: [
                chartConfig.colors.primary,
                chartConfig.colors.secondary,
                chartConfig.colors.success,
                chartConfig.colors.info
            ]
        }
    }
};

// Export chartConfig object
window.chartConfig = chartConfig; 