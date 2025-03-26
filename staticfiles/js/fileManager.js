// File upload and download handling
const fileManager = {
    // Initialize file manager
    init: () => {
        // Initialize file input handlers
        fileManager.initFileInputs();

        // Initialize drag and drop handlers
        fileManager.initDragAndDrop();

        // Initialize file preview handlers
        fileManager.initFilePreviews();
    },

    // Initialize file input handlers
    initFileInputs: () => {
        document.querySelectorAll('input[type="file"]').forEach(input => {
            input.addEventListener('change', (e) => {
                const files = e.target.files;
                if (files.length > 0) {
                    fileManager.handleFileSelection(input, files);
                }
            });
        });
    },

    // Initialize drag and drop handlers
    initDragAndDrop: () => {
        document.querySelectorAll('.drop-zone').forEach(zone => {
            zone.addEventListener('dragover', (e) => {
                e.preventDefault();
                zone.classList.add('drag-over');
            });

            zone.addEventListener('dragleave', () => {
                zone.classList.remove('drag-over');
            });

            zone.addEventListener('drop', (e) => {
                e.preventDefault();
                zone.classList.remove('drag-over');

                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    const input = zone.querySelector('input[type="file"]');
                    if (input) {
                        fileManager.handleFileSelection(input, files);
                    }
                }
            });
        });
    },

    // Initialize file preview handlers
    initFilePreviews: () => {
        document.querySelectorAll('.file-preview').forEach(preview => {
            const input = preview.querySelector('input[type="file"]');
            if (input) {
                input.addEventListener('change', (e) => {
                    const files = e.target.files;
                    if (files.length > 0) {
                        fileManager.showFilePreview(preview, files[0]);
                    }
                });
            }
        });
    },

    // Handle file selection
    handleFileSelection: (input, files) => {
        // Validate file type if specified
        if (input.dataset.accept) {
            const acceptedTypes = input.dataset.accept.split(',');
            const isValidType = Array.from(files).every(file => 
                acceptedTypes.some(type => file.type.match(type.trim()))
            );

            if (!isValidType) {
                notifications.error('Invalid file type. Please select a valid file.');
                input.value = '';
                return;
            }
        }

        // Validate file size if specified
        if (input.dataset.maxSize) {
            const maxSize = parseInt(input.dataset.maxSize);
            const isValidSize = Array.from(files).every(file => file.size <= maxSize);

            if (!isValidSize) {
                notifications.error('File size exceeds the maximum allowed size.');
                input.value = '';
                return;
            }
        }

        // Show file preview if preview container exists
        const preview = input.closest('.file-preview');
        if (preview) {
            fileManager.showFilePreview(preview, files[0]);
        }

        // Trigger custom event for file selection
        const event = new CustomEvent('fileSelected', {
            detail: { files: Array.from(files) }
        });
        input.dispatchEvent(event);
    },

    // Show file preview
    showFilePreview: (preview, file) => {
        const previewImage = preview.querySelector('.preview-image');
        const previewName = preview.querySelector('.preview-name');
        const previewSize = preview.querySelector('.preview-size');

        // Update file name
        if (previewName) {
            previewName.textContent = file.name;
        }

        // Update file size
        if (previewSize) {
            previewSize.textContent = fileManager.formatFileSize(file.size);
        }

        // Show image preview for image files
        if (previewImage && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                previewImage.src = e.target.result;
                previewImage.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    },

    // Format file size
    formatFileSize: (bytes) => {
        if (bytes === 0) return '0 Bytes';

        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));

        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // Upload file
    uploadFile: async (file, endpoint, onProgress = null) => {
        try {
            notifications.showLoading('Uploading file...');

            const formData = new FormData();
            formData.append('file', file);

            const response = await api.uploadFile(endpoint, file, onProgress);

            notifications.success('File uploaded successfully!');
            return response;
        } catch (error) {
            notifications.error('Error uploading file: ' + error.message);
            throw error;
        } finally {
            notifications.hideLoading();
        }
    },

    // Download file
    downloadFile: async (url, filename) => {
        try {
            notifications.showLoading('Downloading file...');

            const response = await fetch(url);
            if (!response.ok) throw new Error('Download failed');

            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(downloadUrl);

            notifications.success('File downloaded successfully!');
        } catch (error) {
            notifications.error('Error downloading file: ' + error.message);
            throw error;
        } finally {
            notifications.hideLoading();
        }
    },

    // Delete file
    deleteFile: async (fileId) => {
        try {
            notifications.confirm('Are you sure you want to delete this file?', async () => {
                notifications.showLoading('Deleting file...');

                await api.delete(`/files/${fileId}/`);
                notifications.success('File deleted successfully!');

                // Remove file element from DOM if it exists
                const fileElement = document.querySelector(`[data-file-id="${fileId}"]`);
                if (fileElement) {
                    fileElement.remove();
                }
            });
        } catch (error) {
            notifications.error('Error deleting file: ' + error.message);
            throw error;
        } finally {
            notifications.hideLoading();
        }
    },

    // Get file extension
    getFileExtension: (filename) => {
        return filename.slice((filename.lastIndexOf('.') - 1 >>> 0) + 1).toLowerCase();
    },

    // Get file icon class
    getFileIconClass: (filename) => {
        const extension = fileManager.getFileExtension(filename);
        const iconMap = {
            // Images
            'jpg': 'bi-file-image',
            'jpeg': 'bi-file-image',
            'png': 'bi-file-image',
            'gif': 'bi-file-image',
            'bmp': 'bi-file-image',
            'svg': 'bi-file-image',

            // Documents
            'pdf': 'bi-file-pdf',
            'doc': 'bi-file-word',
            'docx': 'bi-file-word',
            'xls': 'bi-file-excel',
            'xlsx': 'bi-file-excel',
            'ppt': 'bi-file-ppt',
            'pptx': 'bi-file-ppt',
            'txt': 'bi-file-text',
            'rtf': 'bi-file-text',

            // Archives
            'zip': 'bi-file-zip',
            'rar': 'bi-file-zip',
            '7z': 'bi-file-zip',
            'tar': 'bi-file-zip',
            'gz': 'bi-file-zip',

            // Code
            'html': 'bi-file-code',
            'css': 'bi-file-code',
            'js': 'bi-file-code',
            'php': 'bi-file-code',
            'py': 'bi-file-code',
            'java': 'bi-file-code',
            'cpp': 'bi-file-code',
            'c': 'bi-file-code',

            // Default
            'default': 'bi-file'
        };

        return iconMap[extension] || iconMap.default;
    }
};

// Initialize file manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    fileManager.init();
});

// Export fileManager object
window.fileManager = fileManager; 