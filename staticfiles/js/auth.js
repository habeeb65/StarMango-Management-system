// Authentication and user management
const auth = {
    // Check if user is authenticated
    isAuthenticated: () => {
        return document.cookie.includes('sessionid=');
    },

    // Get current user
    getCurrentUser: async () => {
        try {
            const response = await api.get('/auth/user/');
            return response;
        } catch (error) {
            console.error('Error getting current user:', error);
            return null;
        }
    },

    // Login
    login: async (username, password) => {
        try {
            utils.showLoading();
            const response = await api.post('/auth/login/', {
                username: username,
                password: password
            });

            if (response.success) {
                utils.showAlert('Login successful!');
                window.location.href = '/dashboard/';
            } else {
                utils.showAlert(response.message || 'Login failed', 'danger');
            }
        } catch (error) {
            utils.handleApiError(error);
        } finally {
            utils.hideLoading();
        }
    },

    // Logout
    logout: async () => {
        try {
            utils.showLoading();
            await api.post('/auth/logout/');
            utils.showAlert('Logged out successfully!');
            window.location.href = '/login/';
        } catch (error) {
            utils.handleApiError(error);
        } finally {
            utils.hideLoading();
        }
    },

    // Register
    register: async (userData) => {
        try {
            utils.showLoading();
            const response = await api.post('/auth/register/', userData);

            if (response.success) {
                utils.showAlert('Registration successful! Please login.');
                window.location.href = '/login/';
            } else {
                utils.showAlert(response.message || 'Registration failed', 'danger');
            }
        } catch (error) {
            utils.handleApiError(error);
        } finally {
            utils.hideLoading();
        }
    },

    // Reset password
    resetPassword: async (email) => {
        try {
            utils.showLoading();
            const response = await api.post('/auth/reset-password/', { email });

            if (response.success) {
                utils.showAlert('Password reset instructions sent to your email.');
            } else {
                utils.showAlert(response.message || 'Password reset failed', 'danger');
            }
        } catch (error) {
            utils.handleApiError(error);
        } finally {
            utils.hideLoading();
        }
    },

    // Change password
    changePassword: async (oldPassword, newPassword) => {
        try {
            utils.showLoading();
            const response = await api.post('/auth/change-password/', {
                old_password: oldPassword,
                new_password: newPassword
            });

            if (response.success) {
                utils.showAlert('Password changed successfully!');
            } else {
                utils.showAlert(response.message || 'Password change failed', 'danger');
            }
        } catch (error) {
            utils.handleApiError(error);
        } finally {
            utils.hideLoading();
        }
    },

    // Update profile
    updateProfile: async (profileData) => {
        try {
            utils.showLoading();
            const response = await api.put('/auth/profile/', profileData);

            if (response.success) {
                utils.showAlert('Profile updated successfully!');
            } else {
                utils.showAlert(response.message || 'Profile update failed', 'danger');
            }
        } catch (error) {
            utils.handleApiError(error);
        } finally {
            utils.hideLoading();
        }
    },

    // Initialize auth forms
    initForms: () => {
        // Login form
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const username = loginForm.querySelector('[name="username"]').value;
                const password = loginForm.querySelector('[name="password"]').value;
                await auth.login(username, password);
            });
        }

        // Register form
        const registerForm = document.getElementById('registerForm');
        if (registerForm) {
            registerForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(registerForm);
                const userData = Object.fromEntries(formData.entries());
                await auth.register(userData);
            });
        }

        // Reset password form
        const resetPasswordForm = document.getElementById('resetPasswordForm');
        if (resetPasswordForm) {
            resetPasswordForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const email = resetPasswordForm.querySelector('[name="email"]').value;
                await auth.resetPassword(email);
            });
        }

        // Change password form
        const changePasswordForm = document.getElementById('changePasswordForm');
        if (changePasswordForm) {
            changePasswordForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const oldPassword = changePasswordForm.querySelector('[name="old_password"]').value;
                const newPassword = changePasswordForm.querySelector('[name="new_password"]').value;
                await auth.changePassword(oldPassword, newPassword);
            });
        }

        // Profile form
        const profileForm = document.getElementById('profileForm');
        if (profileForm) {
            profileForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(profileForm);
                const profileData = Object.fromEntries(formData.entries());
                await auth.updateProfile(profileData);
            });
        }
    },

    // Check authentication status
    checkAuth: async () => {
        if (!auth.isAuthenticated()) {
            window.location.href = '/login/';
            return;
        }

        try {
            const user = await auth.getCurrentUser();
            if (!user) {
                window.location.href = '/login/';
                return;
            }

            // Update UI with user info
            const userInfoElements = document.querySelectorAll('[data-user-info]');
            userInfoElements.forEach(element => {
                const field = element.dataset.userInfo;
                if (user[field]) {
                    element.textContent = user[field];
                }
            });
        } catch (error) {
            console.error('Error checking authentication:', error);
            window.location.href = '/login/';
        }
    },

    // Initialize auth functionality
    init: () => {
        // Initialize forms
        auth.initForms();

        // Check authentication status on protected pages
        if (document.body.classList.contains('protected-page')) {
            auth.checkAuth();
        }

        // Add logout button handler
        const logoutButton = document.getElementById('logoutButton');
        if (logoutButton) {
            logoutButton.addEventListener('click', (e) => {
                e.preventDefault();
                auth.logout();
            });
        }
    }
};

// Initialize auth functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    auth.init();
});

// Export auth object
window.auth = auth; 