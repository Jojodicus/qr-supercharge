/**
 * QR Supercharge - Frontend Application
 */

// State management
const state = {
    url: '',
    text: '',
    isLoading: false,
    lastGeneratedUrl: null,
    lastGeneratedText: null,
    debounceTimer: null,
};

// DOM Elements
const elements = {
    urlInput: document.getElementById('url-input'),
    textInput: document.getElementById('text-input'),
    urlError: document.getElementById('url-error'),
    textError: document.getElementById('text-error'),
    qrContainer: document.getElementById('qr-container'),
    qrPlaceholder: document.getElementById('qr-placeholder'),
    qrLoading: document.getElementById('qr-loading'),
    qrResult: document.getElementById('qr-result'),
    qrError: document.getElementById('qr-error'),
    qrImage: document.getElementById('qr-image'),
    qrVersion: document.getElementById('qr-version'),
    qrText: document.getElementById('qr-text'),
    errorMessage: document.getElementById('error-message'),
    downloadBtn: document.getElementById('download-btn'),
};

// Debounce delay in milliseconds
const DEBOUNCE_DELAY = 300;

/**
 * Initialize the application
 */
function init() {
    setupEventListeners();
}

/**
 * Setup all event listeners
 */
function setupEventListeners() {
    // URL input with debouncing
    elements.urlInput.addEventListener('input', handleUrlInput);
    elements.urlInput.addEventListener('blur', validateUrl);
    
    // Text input with debouncing
    elements.textInput.addEventListener('input', handleTextInput);
    
    // Download button
    elements.downloadBtn.addEventListener('click', handleDownload);
    
    // Form submission prevention
    document.getElementById('qr-form').addEventListener('submit', (e) => {
        e.preventDefault();
    });
}

/**
 * Handle URL input with debouncing
 */
function handleUrlInput(e) {
    state.url = e.target.value.trim();
    clearError(elements.urlInput, elements.urlError);
    
    // Clear debounce timer
    if (state.debounceTimer) {
        clearTimeout(state.debounceTimer);
    }
    
    // If URL is empty, reset to placeholder
    if (!state.url) {
        showPlaceholder();
        return;
    }
    
    // Debounce the API call
    state.debounceTimer = setTimeout(() => {
        if (validateUrl()) {
            generateQR();
        }
    }, DEBOUNCE_DELAY);
}

/**
 * Handle text input with debouncing
 */
function handleTextInput(e) {
    state.text = e.target.value.trim();
    clearError(elements.textInput, elements.textError);
    
    // Clear debounce timer
    if (state.debounceTimer) {
        clearTimeout(state.debounceTimer);
    }
    
    // Only generate if URL is valid
    if (state.url && validateUrl()) {
        state.debounceTimer = setTimeout(() => {
            generateQR();
        }, DEBOUNCE_DELAY);
    }
}

/**
 * Validate URL format
 */
function validateUrl() {
    const url = state.url;
    
    if (!url) {
        showError(elements.urlInput, elements.urlError, 'URL is required');
        return false;
    }
    
    try {
        const parsed = new URL(url);
        if (!['http:', 'https:'].includes(parsed.protocol)) {
            showError(elements.urlInput, elements.urlError, 'URL must use HTTP or HTTPS');
            return false;
        }
    } catch {
        showError(elements.urlInput, elements.urlError, 'Please enter a valid URL');
        return false;
    }
    
    return true;
}

/**
 * Generate QR code via API
 */
async function generateQR() {
    // Avoid duplicate requests
    if (state.isLoading) return;
    
    // Check if inputs changed
    if (state.url === state.lastGeneratedUrl && state.text === state.lastGeneratedText) {
        return;
    }
    
    state.isLoading = true;
    showLoading();
    
    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: state.url,
                text: state.text || undefined,
            }),
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            showResult(data);
            state.lastGeneratedUrl = state.url;
            state.lastGeneratedText = state.text;
        } else {
            showErrorState(data.error || 'Failed to generate QR code');
        }
    } catch (error) {
        console.error('Error generating QR:', error);
        showErrorState('Network error. Please try again.');
    } finally {
        state.isLoading = false;
    }
}

/**
 * Show placeholder state
 */
function showPlaceholder() {
    hideAllStates();
    elements.qrPlaceholder.classList.remove('hidden');
}

/**
 * Show loading state
 */
function showLoading() {
    hideAllStates();
    elements.qrLoading.classList.remove('hidden');
}

/**
 * Show result state
 */
function showResult(data) {
    hideAllStates();
    
    elements.qrImage.src = data.qr_code;
    elements.qrVersion.textContent = `v${data.version}`;
    elements.qrText.textContent = data.embedded_text;
    elements.qrResult.classList.remove('hidden');
}

/**
 * Show error state
 */
function showErrorState(message) {
    hideAllStates();
    elements.errorMessage.textContent = message;
    elements.qrError.classList.remove('hidden');
}

/**
 * Hide all states
 */
function hideAllStates() {
    elements.qrPlaceholder.classList.add('hidden');
    elements.qrLoading.classList.add('hidden');
    elements.qrResult.classList.add('hidden');
    elements.qrError.classList.add('hidden');
}

/**
 * Show error on input
 */
function showError(input, errorEl, message) {
    input.classList.add('error');
    errorEl.textContent = message;
    errorEl.classList.add('visible');
}

/**
 * Clear error on input
 */
function clearError(input, errorEl) {
    input.classList.remove('error');
    errorEl.classList.remove('visible');
}

/**
 * Handle download button click
 */
function handleDownload() {
    const img = elements.qrImage;
    if (!img.src) return;
    
    // Create a temporary link
    const link = document.createElement('a');
    link.href = img.src;
    
    // Generate filename from URL
    let filename = 'qr-code.png';
    try {
        const url = new URL(state.url);
        const domain = url.hostname.replace(/^www\./, '').replace(/\./g, '_');
        filename = `${domain}.png`;
    } catch {
        // Use default filename
    }
    
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', init);
