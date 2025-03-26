// Table utility functions
const tableUtils = {
    // Initialize table functionality
    init: (tableId) => {
        const table = document.getElementById(tableId);
        if (!table) return;

        // Add sorting functionality
        tableUtils.addSorting(table);

        // Add filtering functionality
        tableUtils.addFiltering(table);

        // Add pagination functionality
        tableUtils.addPagination(table);

        // Add row selection functionality
        tableUtils.addRowSelection(table);
    },

    // Add sorting functionality
    addSorting: (table) => {
        const headers = table.querySelectorAll('th[data-sortable]');
        headers.forEach(header => {
            header.addEventListener('click', () => {
                const column = header.cellIndex;
                const type = header.dataset.sortable;
                tableUtils.sortTable(table, column, type);
            });
        });
    },

    // Sort table
    sortTable: (table, column, type) => {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const header = table.querySelector(`th:nth-child(${column + 1})`);
        const currentOrder = header.dataset.order || 'asc';

        // Update sort order
        header.dataset.order = currentOrder === 'asc' ? 'desc' : 'asc';

        // Sort rows
        rows.sort((a, b) => {
            const aValue = a.cells[column].textContent.trim();
            const bValue = b.cells[column].textContent.trim();

            let comparison = 0;

            switch (type) {
                case 'number':
                    comparison = parseFloat(aValue) - parseFloat(bValue);
                    break;
                case 'date':
                    comparison = new Date(aValue) - new Date(bValue);
                    break;
                case 'currency':
                    comparison = parseFloat(aValue.replace(/[^0-9.-]+/g, '')) - 
                                parseFloat(bValue.replace(/[^0-9.-]+/g, ''));
                    break;
                default:
                    comparison = aValue.localeCompare(bValue);
            }

            return currentOrder === 'asc' ? comparison : -comparison;
        });

        // Update table
        rows.forEach(row => tbody.appendChild(row));
    },

    // Add filtering functionality
    addFiltering: (table) => {
        const filterInput = document.createElement('input');
        filterInput.type = 'text';
        filterInput.className = 'form-control mb-3';
        filterInput.placeholder = 'Filter table...';
        table.parentNode.insertBefore(filterInput, table);

        filterInput.addEventListener('input', () => {
            const searchTerm = filterInput.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr');

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        });
    },

    // Add pagination functionality
    addPagination: (table) => {
        const rows = table.querySelectorAll('tbody tr');
        const rowsPerPage = 10;
        const pageCount = Math.ceil(rows.length / rowsPerPage);
        let currentPage = 1;

        // Create pagination controls
        const pagination = document.createElement('div');
        pagination.className = 'd-flex justify-content-between align-items-center mt-3';
        pagination.innerHTML = `
            <div class="text-muted">
                Showing ${(currentPage - 1) * rowsPerPage + 1} to ${Math.min(currentPage * rowsPerPage, rows.length)} of ${rows.length} entries
            </div>
            <nav>
                <ul class="pagination mb-0">
                    <li class="page-item">
                        <a class="page-link" href="#" data-page="prev">Previous</a>
                    </li>
                    <li class="page-item">
                        <a class="page-link" href="#" data-page="next">Next</a>
                    </li>
                </ul>
            </nav>
        `;
        table.parentNode.appendChild(pagination);

        // Update table display
        const updateTable = () => {
            rows.forEach((row, index) => {
                const start = (currentPage - 1) * rowsPerPage;
                const end = currentPage * rowsPerPage;
                row.style.display = index >= start && index < end ? '' : 'none';
            });

            // Update pagination info
            pagination.querySelector('.text-muted').textContent = 
                `Showing ${(currentPage - 1) * rowsPerPage + 1} to ${Math.min(currentPage * rowsPerPage, rows.length)} of ${rows.length} entries`;
        };

        // Handle pagination clicks
        pagination.addEventListener('click', (e) => {
            if (e.target.tagName === 'A') {
                e.preventDefault();
                const action = e.target.dataset.page;

                if (action === 'prev' && currentPage > 1) {
                    currentPage--;
                } else if (action === 'next' && currentPage < pageCount) {
                    currentPage++;
                }

                updateTable();
            }
        });

        // Initial display
        updateTable();
    },

    // Add row selection functionality
    addRowSelection: (table) => {
        const rows = table.querySelectorAll('tbody tr');
        const selectAllCheckbox = document.createElement('input');
        selectAllCheckbox.type = 'checkbox';
        selectAllCheckbox.className = 'form-check-input';
        const headerCell = document.createElement('th');
        headerCell.appendChild(selectAllCheckbox);
        table.querySelector('thead tr').insertBefore(headerCell, table.querySelector('thead tr').firstChild);

        // Add checkbox to each row
        rows.forEach(row => {
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.className = 'form-check-input';
            const cell = document.createElement('td');
            cell.appendChild(checkbox);
            row.insertBefore(cell, row.firstChild);
        });

        // Handle select all
        selectAllCheckbox.addEventListener('change', () => {
            const checkboxes = table.querySelectorAll('tbody input[type="checkbox"]');
            checkboxes.forEach(checkbox => {
                checkbox.checked = selectAllCheckbox.checked;
            });
        });

        // Handle individual row selection
        rows.forEach(row => {
            const checkbox = row.querySelector('input[type="checkbox"]');
            checkbox.addEventListener('change', () => {
                const checkboxes = table.querySelectorAll('tbody input[type="checkbox"]');
                const allChecked = Array.from(checkboxes).every(cb => cb.checked);
                selectAllCheckbox.checked = allChecked;
            });
        });
    },

    // Export table to CSV
    exportToCsv: (table, filename) => {
        const rows = table.querySelectorAll('tr');
        const csv = [];

        rows.forEach(row => {
            const cells = row.querySelectorAll('td, th');
            const rowData = Array.from(cells).map(cell => {
                let text = cell.textContent.trim();
                // Escape commas and quotes
                if (text.includes(',') || text.includes('"')) {
                    text = `"${text.replace(/"/g, '""')}"`;
                }
                return text;
            });
            csv.push(rowData.join(','));
        });

        const csvContent = csv.join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = filename;
        link.click();
    },

    // Export table to Excel
    exportToExcel: (table, filename) => {
        const rows = table.querySelectorAll('tr');
        const excel = [];

        rows.forEach(row => {
            const cells = row.querySelectorAll('td, th');
            const rowData = Array.from(cells).map(cell => cell.textContent.trim());
            excel.push(rowData.join('\t'));
        });

        const excelContent = excel.join('\n');
        const blob = new Blob([excelContent], { type: 'application/vnd.ms-excel' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = filename;
        link.click();
    }
};

// Export tableUtils object
window.tableUtils = tableUtils; 