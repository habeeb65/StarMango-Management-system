// Inventory management functionality
const inventoryManager = {
    // Initialize inventory page
    init: () => {
        const searchInput = document.getElementById('search');
        const categorySelect = document.getElementById('category');
        const stockStatusSelect = document.getElementById('stock_status');

        if (searchInput) {
            searchInput.addEventListener('input', inventoryManager.handleSearch);
        }

        if (categorySelect) {
            categorySelect.addEventListener('change', inventoryManager.handleFilter);
        }

        if (stockStatusSelect) {
            stockStatusSelect.addEventListener('change', inventoryManager.handleFilter);
        }

        // Initialize item actions
        inventoryManager.initItemActions();
    },

    // Handle search input
    handleSearch: (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const rows = document.querySelectorAll('table tbody tr');

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    },

    // Handle filter changes
    handleFilter: () => {
        const searchTerm = document.getElementById('search').value.toLowerCase();
        const categoryValue = document.getElementById('category').value;
        const stockStatusValue = document.getElementById('stock_status').value;
        const rows = document.querySelectorAll('table tbody tr');

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const category = row.querySelector('td:nth-child(2)').textContent;
            const stockStatus = row.querySelector('td:nth-child(6)').textContent;

            const matchesSearch = text.includes(searchTerm);
            const matchesCategory = !categoryValue || category === categoryValue;
            const matchesStockStatus = !stockStatusValue || stockStatus.includes(stockStatusValue);

            row.style.display = matchesSearch && matchesCategory && matchesStockStatus ? '' : 'none';
        });
    },

    // Initialize item actions
    initItemActions: () => {
        // Edit item
        document.querySelectorAll('.btn-edit').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const itemId = e.target.closest('tr').dataset.itemId;
                window.location.href = `/inventory/edit/${itemId}/`;
            });
        });

        // Delete item
        document.querySelectorAll('.btn-delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const itemId = e.target.closest('tr').dataset.itemId;
                inventoryManager.handleDelete(itemId);
            });
        });
    },

    // Handle item deletion
    handleDelete: async (itemId) => {
        if (!confirm('Are you sure you want to delete this item?')) {
            return;
        }

        utils.showLoading();

        try {
            const response = await fetch(`/inventory/delete/${itemId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            });

            if (response.ok) {
                utils.showAlert('Item deleted successfully!');
                window.location.reload();
            } else {
                const data = await response.json();
                utils.showAlert(data.error || 'Error deleting item', 'danger');
            }
        } catch (error) {
            utils.showAlert('Error deleting item', 'danger');
        } finally {
            utils.hideLoading();
        }
    },

    // Initialize add item form
    initAddItemForm: () => {
        const form = document.getElementById('addItemForm');
        if (!form) return;

        form.addEventListener('submit', inventoryManager.handleAddItem);
    },

    // Handle add item form submission
    handleAddItem: async (e) => {
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
                utils.showAlert('Item added successfully!');
                window.location.href = '/inventory/';
            } else {
                const data = await response.json();
                utils.showAlert(data.error || 'Error adding item', 'danger');
            }
        } catch (error) {
            utils.showAlert('Error adding item', 'danger');
        } finally {
            utils.hideLoading();
        }
    },

    // Initialize edit item form
    initEditItemForm: () => {
        const form = document.getElementById('editItemForm');
        if (!form) return;

        form.addEventListener('submit', inventoryManager.handleEditItem);
    },

    // Handle edit item form submission
    handleEditItem: async (e) => {
        e.preventDefault();

        if (!formValidation.validateRequired(e.target)) {
            utils.showAlert('Please fill in all required fields', 'danger');
            return;
        }

        utils.showLoading();

        try {
            const formData = new FormData(e.target);
            const itemId = e.target.dataset.itemId;
            const response = await fetch(`/inventory/edit/${itemId}/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            });

            if (response.ok) {
                utils.showAlert('Item updated successfully!');
                window.location.href = '/inventory/';
            } else {
                const data = await response.json();
                utils.showAlert(data.error || 'Error updating item', 'danger');
            }
        } catch (error) {
            utils.showAlert('Error updating item', 'danger');
        } finally {
            utils.hideLoading();
        }
    }
};

// Initialize inventory functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    inventoryManager.init();
    inventoryManager.initAddItemForm();
    inventoryManager.initEditItemForm();
}); 