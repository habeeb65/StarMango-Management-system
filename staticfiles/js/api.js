// API request handling
const api = {
    // Base URL for API endpoints
    baseUrl: '/api',

    // Default headers
    defaultHeaders: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    },

    // Get CSRF token
    getCsrfToken: () => {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    },

    // Add CSRF token to headers
    addCsrfToken: (headers) => {
        headers['X-CSRFToken'] = api.getCsrfToken();
        return headers;
    },

    // Handle API response
    handleResponse: async (response) => {
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'An error occurred');
        }
        return response.json();
    },

    // GET request
    get: async (endpoint, params = {}) => {
        try {
            const queryString = new URLSearchParams(params).toString();
            const url = `${api.baseUrl}${endpoint}${queryString ? `?${queryString}` : ''}`;
            
            const response = await fetch(url, {
                method: 'GET',
                headers: api.addCsrfToken({ ...api.defaultHeaders })
            });

            return api.handleResponse(response);
        } catch (error) {
            utils.handleApiError(error);
            throw error;
        }
    },

    // POST request
    post: async (endpoint, data = {}) => {
        try {
            const response = await fetch(`${api.baseUrl}${endpoint}`, {
                method: 'POST',
                headers: api.addCsrfToken({ ...api.defaultHeaders }),
                body: JSON.stringify(data)
            });

            return api.handleResponse(response);
        } catch (error) {
            utils.handleApiError(error);
            throw error;
        }
    },

    // PUT request
    put: async (endpoint, data = {}) => {
        try {
            const response = await fetch(`${api.baseUrl}${endpoint}`, {
                method: 'PUT',
                headers: api.addCsrfToken({ ...api.defaultHeaders }),
                body: JSON.stringify(data)
            });

            return api.handleResponse(response);
        } catch (error) {
            utils.handleApiError(error);
            throw error;
        }
    },

    // DELETE request
    delete: async (endpoint) => {
        try {
            const response = await fetch(`${api.baseUrl}${endpoint}`, {
                method: 'DELETE',
                headers: api.addCsrfToken({ ...api.defaultHeaders })
            });

            return api.handleResponse(response);
        } catch (error) {
            utils.handleApiError(error);
            throw error;
        }
    },

    // Upload file
    uploadFile: async (endpoint, file, onProgress = null) => {
        try {
            const formData = new FormData();
            formData.append('file', file);

            const xhr = new XMLHttpRequest();
            xhr.open('POST', `${api.baseUrl}${endpoint}`);
            xhr.setRequestHeader('X-CSRFToken', api.getCsrfToken());

            if (onProgress) {
                xhr.upload.addEventListener('progress', (event) => {
                    if (event.lengthComputable) {
                        const progress = (event.loaded / event.total) * 100;
                        onProgress(progress);
                    }
                });
            }

            return new Promise((resolve, reject) => {
                xhr.onload = () => {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        resolve(JSON.parse(xhr.responseText));
                    } else {
                        reject(new Error(xhr.responseText));
                    }
                };

                xhr.onerror = () => {
                    reject(new Error('Network error occurred'));
                };

                xhr.send(formData);
            });
        } catch (error) {
            utils.handleApiError(error);
            throw error;
        }
    },

    // API endpoints
    endpoints: {
        // Inventory endpoints
        inventory: {
            list: '/inventory/',
            detail: (id) => `/inventory/${id}/`,
            create: '/inventory/create/',
            update: (id) => `/inventory/${id}/update/`,
            delete: (id) => `/inventory/${id}/delete/`,
            categories: '/inventory/categories/',
            lowStock: '/inventory/low-stock/'
        },

        // Sales endpoints
        sales: {
            list: '/sales/',
            detail: (id) => `/sales/${id}/`,
            create: '/sales/create/',
            update: (id) => `/sales/${id}/update/`,
            delete: (id) => `/sales/${id}/delete/`,
            today: '/sales/today/',
            thisWeek: '/sales/this-week/',
            thisMonth: '/sales/this-month/'
        },

        // Reports endpoints
        reports: {
            sales: '/reports/sales/',
            inventory: '/reports/inventory/',
            financial: '/reports/financial/',
            export: (type) => `/reports/export/${type}/`
        },

        // Dashboard endpoints
        dashboard: {
            stats: '/dashboard/stats/',
            recentActivity: '/dashboard/recent-activity/',
            lowStockAlerts: '/dashboard/low-stock-alerts/'
        }
    },

    // Example usage methods
    methods: {
        // Inventory methods
        getInventoryList: (params) => api.get(api.endpoints.inventory.list, params),
        getInventoryItem: (id) => api.get(api.endpoints.inventory.detail(id)),
        createInventoryItem: (data) => api.post(api.endpoints.inventory.create, data),
        updateInventoryItem: (id, data) => api.put(api.endpoints.inventory.update(id), data),
        deleteInventoryItem: (id) => api.delete(api.endpoints.inventory.delete(id)),
        getInventoryCategories: () => api.get(api.endpoints.inventory.categories),
        getLowStockItems: () => api.get(api.endpoints.inventory.lowStock),

        // Sales methods
        getSalesList: (params) => api.get(api.endpoints.sales.list, params),
        getSaleDetail: (id) => api.get(api.endpoints.sales.detail(id)),
        createSale: (data) => api.post(api.endpoints.sales.create, data),
        updateSale: (id, data) => api.put(api.endpoints.sales.update(id), data),
        deleteSale: (id) => api.delete(api.endpoints.sales.delete(id)),
        getTodaySales: () => api.get(api.endpoints.sales.today),
        getThisWeekSales: () => api.get(api.endpoints.sales.thisWeek),
        getThisMonthSales: () => api.get(api.endpoints.sales.thisMonth),

        // Reports methods
        getSalesReport: (params) => api.get(api.endpoints.reports.sales, params),
        getInventoryReport: (params) => api.get(api.endpoints.reports.inventory, params),
        getFinancialReport: (params) => api.get(api.endpoints.reports.financial, params),
        exportReport: (type) => api.get(api.endpoints.reports.export(type)),

        // Dashboard methods
        getDashboardStats: () => api.get(api.endpoints.dashboard.stats),
        getRecentActivity: () => api.get(api.endpoints.dashboard.recentActivity),
        getLowStockAlerts: () => api.get(api.endpoints.dashboard.lowStockAlerts)
    }
};

// Export api object
window.api = api; 