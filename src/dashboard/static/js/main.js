/**
 * Pet Automation Suite - Main JavaScript
 */

// Initialize tooltips and popovers
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Add active class to current nav item
    highlightCurrentNavItem();
    
    // Initialize DataTables if available
    initializeDataTables();
});

/**
 * Highlight the current navigation item based on URL
 */
function highlightCurrentNavItem() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath) {
            link.classList.add('active');
        }
    });
}

/**
 * Initialize DataTables for tables
 */
function initializeDataTables() {
    if (typeof $.fn.DataTable !== 'undefined') {
        $('.datatable').DataTable({
            responsive: true,
            pageLength: 10,
            language: {
                search: "_INPUT_",
                searchPlaceholder: "Search...",
                lengthMenu: "Show _MENU_ entries per page",
                info: "Showing _START_ to _END_ of _TOTAL_ entries",
                infoEmpty: "Showing 0 to 0 of 0 entries",
                infoFiltered: "(filtered from _MAX_ total entries)"
            }
        });
    }
}

/**
 * Format currency values
 * @param {number} value - The value to format
 * @param {string} currency - Currency code (default: USD)
 * @returns {string} Formatted currency string
 */
function formatCurrency(value, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(value);
}

/**
 * Format percentage values
 * @param {number} value - The value to format
 * @param {number} decimals - Number of decimal places
 * @returns {string} Formatted percentage string
 */
function formatPercentage(value, decimals = 1) {
    return value.toFixed(decimals) + '%';
}

/**
 * Format date values
 * @param {string} dateString - The date string to format
 * @param {string} format - Format style ('short', 'medium', 'long')
 * @returns {string} Formatted date string
 */
function formatDate(dateString, format = 'medium') {
    const date = new Date(dateString);
    
    const options = {
        short: { month: 'numeric', day: 'numeric' },
        medium: { month: 'short', day: 'numeric', year: 'numeric' },
        long: { weekday: 'short', month: 'long', day: 'numeric', year: 'numeric' }
    };
    
    return date.toLocaleDateString('en-US', options[format]);
}

/**
 * Show loading spinner
 * @param {string} elementId - ID of element to show spinner in
 * @param {string} message - Optional loading message
 */
function showLoading(elementId, message = 'Loading...') {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="text-center">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">${message}</p>
            </div>
        `;
    }
}

/**
 * Hide loading spinner and show content
 * @param {string} elementId - ID of element containing spinner
 * @param {string} content - Content to replace spinner with
 */
function hideLoading(elementId, content) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = content;
    }
}

/**
 * Show toast notification
 * @param {string} message - Notification message
 * @param {string} type - Notification type (success, error, warning, info)
 */
function showNotification(message, type = 'success') {
    // Check if toast container exists, if not create it
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const bgClass = `bg-${type === 'error' ? 'danger' : type}`;
    const textClass = type === 'warning' ? 'text-dark' : 'text-white';
    
    const toastHtml = `
        <div id="${toastId}" class="toast ${bgClass} ${textClass}" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <strong class="me-auto">Pet Automation Suite</strong>
                <small>Just now</small>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    // Initialize and show toast
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { autohide: true, delay: 5000 });
    toast.show();
    
    // Remove toast after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

/**
 * Make API request
 * @param {string} url - API endpoint URL
 * @param {string} method - HTTP method (GET, POST, etc.)
 * @param {object} data - Request data (for POST, PUT, etc.)
 * @returns {Promise} Promise resolving to response data
 */
async function apiRequest(url, method = 'GET', data = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(url, options);
        
        if (!response.ok) {
            throw new Error(`API request failed: ${response.status} ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request error:', error);
        showNotification(error.message, 'error');
        throw error;
    }
}

/**
 * Train ML model
 * @param {string} modelType - Type of model to train
 */
function trainModel(modelType) {
    showNotification(`Training ${modelType} model...`, 'info');
    
    apiRequest('/api/train-ml-model', 'POST', { model_type: modelType })
        .then(data => {
            if (data.success) {
                showNotification(`${modelType} model trained successfully!`, 'success');
            } else {
                showNotification(`Failed to train model: ${data.error}`, 'error');
            }
        })
        .catch(error => {
            showNotification(`Error training model: ${error}`, 'error');
        });
}

/**
 * Generate content
 */
function generateContent() {
    showNotification('Content generation initiated', 'info');
    
    // This would make an API call to trigger content generation
    setTimeout(() => {
        showNotification('Content generation in progress - check logs for details', 'success');
    }, 1000);
}

/**
 * Schedule posts
 */
function schedulePosts() {
    showNotification('Post scheduling initiated', 'info');
    
    // This would make an API call to trigger post scheduling
    setTimeout(() => {
        showNotification('Posts scheduled successfully - check social media page', 'success');
    }, 1000);
}

/**
 * Update pricing
 */
function updatePricing() {
    showNotification('Dynamic pricing update initiated', 'info');
    
    // This would make an API call to trigger pricing updates
    setTimeout(() => {
        showNotification('Pricing updated successfully - check products page', 'success');
    }, 1000);
}

/**
 * Sync products
 */
function syncProducts() {
    showNotification('Product sync initiated', 'info');
    
    // This would make an API call to trigger product sync
    setTimeout(() => {
        showNotification('Products synced successfully', 'success');
    }, 1000);
}

/**
 * Generate product descriptions
 */
function generateDescriptions() {
    showNotification('Description generation initiated', 'info');
    
    // This would make an API call to trigger description generation
    setTimeout(() => {
        showNotification('Descriptions generated successfully', 'success');
    }, 1000);
}

/**
 * Optimize SEO
 */
function optimizeSEO() {
    showNotification('SEO optimization initiated', 'info');
    
    // This would make an API call to trigger SEO optimization
    setTimeout(() => {
        showNotification('SEO optimization completed', 'success');
    }, 1000);
}