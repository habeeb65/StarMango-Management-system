// Form validation functions
const formValidation = {
    // Validate required fields
    validateRequired: (form) => {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                isValid = false;
            } else {
                field.classList.remove('is-invalid');
            }
        });

        return isValid;
    },

    // Validate numeric fields
    validateNumeric: (field) => {
        const value = field.value.trim();
        if (value === '') return true;

        const number = parseFloat(value);
        if (isNaN(number)) {
            field.classList.add('is-invalid');
            return false;
        }

        field.classList.remove('is-invalid');
        return true;
    },

    // Validate email format
    validateEmail: (field) => {
        const email = field.value.trim();
        if (email === '') return true;

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            field.classList.add('is-invalid');
            return false;
        }

        field.classList.remove('is-invalid');
        return true;
    },

    // Validate phone number format
    validatePhone: (field) => {
        const phone = field.value.trim();
        if (phone === '') return true;

        const phoneRegex = /^\+?[\d\s-()]{10,}$/;
        if (!phoneRegex.test(phone)) {
            field.classList.add('is-invalid');
            return false;
        }

        field.classList.remove('is-invalid');
        return true;
    },

    // Validate date format
    validateDate: (field) => {
        const date = field.value.trim();
        if (date === '') return true;

        const dateObj = new Date(date);
        if (isNaN(dateObj.getTime())) {
            field.classList.add('is-invalid');
            return false;
        }

        field.classList.remove('is-invalid');
        return true;
    },

    // Validate date range
    validateDateRange: (startField, endField) => {
        const startDate = new Date(startField.value);
        const endDate = new Date(endField.value);

        if (startDate > endDate) {
            startField.classList.add('is-invalid');
            endField.classList.add('is-invalid');
            return false;
        }

        startField.classList.remove('is-invalid');
        endField.classList.remove('is-invalid');
        return true;
    },

    // Validate minimum value
    validateMinValue: (field, min) => {
        const value = parseFloat(field.value);
        if (isNaN(value)) return true;

        if (value < min) {
            field.classList.add('is-invalid');
            return false;
        }

        field.classList.remove('is-invalid');
        return true;
    },

    // Validate maximum value
    validateMaxValue: (field, max) => {
        const value = parseFloat(field.value);
        if (isNaN(value)) return true;

        if (value > max) {
            field.classList.add('is-invalid');
            return false;
        }

        field.classList.remove('is-invalid');
        return true;
    },

    // Validate password strength
    validatePassword: (field) => {
        const password = field.value;
        if (password === '') return true;

        const hasUpperCase = /[A-Z]/.test(password);
        const hasLowerCase = /[a-z]/.test(password);
        const hasNumbers = /\d/.test(password);
        const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
        const isLongEnough = password.length >= 8;

        if (!hasUpperCase || !hasLowerCase || !hasNumbers || !hasSpecialChar || !isLongEnough) {
            field.classList.add('is-invalid');
            return false;
        }

        field.classList.remove('is-invalid');
        return true;
    },

    // Validate password match
    validatePasswordMatch: (passwordField, confirmField) => {
        if (passwordField.value !== confirmField.value) {
            passwordField.classList.add('is-invalid');
            confirmField.classList.add('is-invalid');
            return false;
        }

        passwordField.classList.remove('is-invalid');
        confirmField.classList.remove('is-invalid');
        return true;
    },

    // Validate file type
    validateFileType: (field, allowedTypes) => {
        const file = field.files[0];
        if (!file) return true;

        if (!allowedTypes.includes(file.type)) {
            field.classList.add('is-invalid');
            return false;
        }

        field.classList.remove('is-invalid');
        return true;
    },

    // Validate file size
    validateFileSize: (field, maxSize) => {
        const file = field.files[0];
        if (!file) return true;

        if (file.size > maxSize) {
            field.classList.add('is-invalid');
            return false;
        }

        field.classList.remove('is-invalid');
        return true;
    },

    // Validate URL format
    validateUrl: (field) => {
        const url = field.value.trim();
        if (url === '') return true;

        try {
            new URL(url);
            field.classList.remove('is-invalid');
            return true;
        } catch (e) {
            field.classList.add('is-invalid');
            return false;
        }
    },

    // Validate credit card number
    validateCreditCard: (field) => {
        const number = field.value.trim();
        if (number === '') return true;

        // Luhn algorithm
        let sum = 0;
        let isEven = false;

        for (let i = number.length - 1; i >= 0; i--) {
            let digit = parseInt(number[i], 10);

            if (isEven) {
                digit *= 2;
                if (digit > 9) {
                    digit -= 9;
                }
            }

            sum += digit;
            isEven = !isEven;
        }

        if (sum % 10 !== 0) {
            field.classList.add('is-invalid');
            return false;
        }

        field.classList.remove('is-invalid');
        return true;
    }
};

// Export formValidation object
window.formValidation = formValidation; 