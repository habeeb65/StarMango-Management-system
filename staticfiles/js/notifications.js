// Notifications and alerts handling
const notifications = {
    // Notification types
    types: {
        success: 'success',
        error: 'danger',
        warning: 'warning',
        info: 'info'
    },

    // Notification container
    container: null,

    // Initialize notifications
    init: () => {
        // Create notification container if it doesn't exist
        if (!notifications.container) {
            notifications.container = document.createElement('div');
            notifications.container.id = 'notificationContainer';
            notifications.container.className = 'position-fixed top-0 end-0 p-3';
            notifications.container.style.zIndex = '9999';
            document.body.appendChild(notifications.container);
        }
    },

    // Show notification
    show: (message, type = notifications.types.info, duration = 5000) => {
        notifications.init();

        const notification = document.createElement('div');
        notification.className = `toast align-items-center text-white bg-${type} border-0`;
        notification.setAttribute('role', 'alert');
        notification.setAttribute('aria-live', 'assertive');
        notification.setAttribute('aria-atomic', 'true');

        notification.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        notifications.container.appendChild(notification);

        // Initialize Bootstrap toast
        const toast = new bootstrap.Toast(notification, {
            delay: duration
        });

        // Show toast
        toast.show();

        // Remove toast after it's hidden
        notification.addEventListener('hidden.bs.toast', () => {
            notification.remove();
        });
    },

    // Show success notification
    success: (message, duration) => {
        notifications.show(message, notifications.types.success, duration);
    },

    // Show error notification
    error: (message, duration) => {
        notifications.show(message, notifications.types.error, duration);
    },

    // Show warning notification
    warning: (message, duration) => {
        notifications.show(message, notifications.types.warning, duration);
    },

    // Show info notification
    info: (message, duration) => {
        notifications.show(message, notifications.types.info, duration);
    },

    // Show confirmation dialog
    confirm: (message, callback) => {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.setAttribute('tabindex', '-1');
        modal.setAttribute('aria-hidden', 'true');

        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Confirm</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="confirmButton">Confirm</button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();

        // Handle confirmation
        const confirmButton = modal.querySelector('#confirmButton');
        confirmButton.addEventListener('click', () => {
            modalInstance.hide();
            if (callback) callback();
        });

        // Clean up modal after it's hidden
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    },

    // Show loading spinner
    showLoading: (message = 'Loading...') => {
        const spinner = document.createElement('div');
        spinner.id = 'loadingSpinner';
        spinner.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center';
        spinner.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        spinner.style.zIndex = '9999';

        spinner.innerHTML = `
            <div class="text-center text-white">
                <div class="spinner-border mb-3" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <div>${message}</div>
            </div>
        `;

        document.body.appendChild(spinner);
    },

    // Hide loading spinner
    hideLoading: () => {
        const spinner = document.getElementById('loadingSpinner');
        if (spinner) {
            spinner.remove();
        }
    },

    // Show tooltip
    showTooltip: (element, message) => {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip fade show';
        tooltip.setAttribute('role', 'tooltip');
        tooltip.style.position = 'absolute';
        tooltip.style.zIndex = '9999';

        tooltip.innerHTML = `
            <div class="tooltip-arrow"></div>
            <div class="tooltip-inner">${message}</div>
        `;

        element.appendChild(tooltip);

        // Position tooltip
        const rect = element.getBoundingClientRect();
        tooltip.style.top = `${rect.top - tooltip.offsetHeight - 5}px`;
        tooltip.style.left = `${rect.left + (rect.width - tooltip.offsetWidth) / 2}px`;

        // Remove tooltip after delay
        setTimeout(() => {
            tooltip.remove();
        }, 3000);
    },

    // Show popover
    showPopover: (element, title, content) => {
        const popover = document.createElement('div');
        popover.className = 'popover fade show';
        popover.setAttribute('role', 'tooltip');
        popover.style.position = 'absolute';
        popover.style.zIndex = '9999';

        popover.innerHTML = `
            <div class="popover-arrow"></div>
            <h3 class="popover-header">${title}</h3>
            <div class="popover-body">${content}</div>
        `;

        element.appendChild(popover);

        // Position popover
        const rect = element.getBoundingClientRect();
        popover.style.top = `${rect.top - popover.offsetHeight - 5}px`;
        popover.style.left = `${rect.left + (rect.width - popover.offsetWidth) / 2}px`;

        // Remove popover after delay
        setTimeout(() => {
            popover.remove();
        }, 5000);
    }
};

// Initialize notifications when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    notifications.init();
});

// Export notifications object
window.notifications = notifications; 