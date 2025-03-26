// Sales functionality
const salesManager = {
    // Initialize sales form
    initSalesForm: () => {
        const form = document.getElementById('saleForm');
        if (!form) return;

        // Add new item row
        const addItemBtn = document.getElementById('addItemRow');
        if (addItemBtn) {
            addItemBtn.addEventListener('click', salesManager.addItemRow);
        }

        // Remove item row
        document.addEventListener('click', (e) => {
            if (e.target.closest('.remove-item')) {
                salesManager.removeItemRow(e);
            }
        });

        // Calculate totals on input changes
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('item-select') || 
                e.target.classList.contains('quantity')) {
                salesManager.calculateItemTotal(e.target.closest('tr'));
            }
        });

        // Form submission
        form.addEventListener('submit', salesManager.handleFormSubmit);
    },

    // Add new item row
    addItemRow: () => {
        const tbody = document.querySelector('#itemsTable tbody');
        const newRow = tbody.rows[0].cloneNode(true);
        
        // Clear values
        newRow.querySelector('.item-select').value = '';
        newRow.querySelector('.quantity').value = '';
        newRow.querySelector('.unit-price').value = '';
        newRow.querySelector('.item-total').value = '';
        
        tbody.appendChild(newRow);
    },

    // Remove item row
    removeItemRow: (event) => {
        const tbody = document.querySelector('#itemsTable tbody');
        if (tbody.rows.length > 1) {
            event.target.closest('tr').remove();
            salesManager.calculateTotal();
        }
    },

    // Calculate item total
    calculateItemTotal: (row) => {
        const quantity = parseFloat(row.querySelector('.quantity').value) || 0;
        const unitPrice = parseFloat(row.querySelector('.unit-price').value) || 0;
        row.querySelector('.item-total').value = (quantity * unitPrice).toFixed(2);
        salesManager.calculateTotal();
    },

    // Calculate total amount
    calculateTotal: () => {
        const totals = Array.from(document.querySelectorAll('.item-total'))
            .map(input => parseFloat(input.value) || 0);
        const total = totals.reduce((sum, value) => sum + value, 0);
        document.getElementById('totalAmount').textContent = total.toFixed(2);
    },

    // Handle form submission
    handleFormSubmit: async (e) => {
        e.preventDefault();
        
        if (!formValidation.validateRequired(e.target)) {
            utils.showAlert('Please fill in all required fields', 'danger');
            return;
        }

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
                utils.showAlert('Sale completed successfully!');
                window.location.href = '/sales/';
            } else {
                const data = await response.json();
                utils.showAlert(data.error || 'Error creating sale', 'danger');
            }
        } catch (error) {
            utils.showAlert('Error creating sale', 'danger');
        } finally {
            utils.hideLoading();
        }
    }
};

// Initialize sales functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    salesManager.initSalesForm();
}); 