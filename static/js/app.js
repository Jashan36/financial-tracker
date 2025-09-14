// Configuration object
const CONFIG = {
    ALLOWED_TYPES: ['.csv', '.pdf'],
    MAX_FILE_SIZE: 16 * 1024 * 1024, // 16MB
    API_TIMEOUT: 60000, // 60 seconds
    CHUNK_SIZE: 1000 // Process data in chunks
};

// Global variables
let currentTransactions = [];
let currentAnalysis = {};
let currentRecommendations = {};
let sessionId = null;
let isLoading = false;
let currencyGroups = new Map(); // Store transactions grouped by currency

// Function to analyze transactions and group by currency
function analyzeTransactionsByCurrency(transactions) {
    const groups = new Map();
    const currencySums = new Map();
    const currencyFrequency = new Map();
    
    // Group transactions by currency
    transactions.forEach(transaction => {
        if (!transaction.currency) {
            console.warn('Transaction missing currency:', transaction);
            return;
        }
        
        const currency = transaction.currency;
        if (!groups.has(currency)) {
            groups.set(currency, []);
            currencySums.set(currency, 0);
            currencyFrequency.set(currency, 0);
        }
        groups.get(currency).push(transaction);
        currencySums.set(currency, currencySums.get(currency) + Math.abs(transaction.amount));
        currencyFrequency.set(currency, currencyFrequency.get(currency) + 1);
    });
    
    // Determine primary currency based on frequency and total value
    let primaryCurrency = '';
    let maxScore = -1;
    
    currencySums.forEach((sum, currency) => {
        const frequency = currencyFrequency.get(currency);
        // Score is weighted combination of frequency and total value
        const score = (frequency * 0.7) + (sum * 0.3);
        if (score > maxScore) {
            maxScore = score;
            primaryCurrency = currency;
        }
    });
    
    // If no primary currency found (empty dataset), use the first available or null
    if (!primaryCurrency && groups.size > 0) {
        primaryCurrency = groups.keys().next().value;
    }
    
    return {
        groups: groups,
        primaryCurrency: primaryCurrency,
        currencySums: currencySums,
        currencyFrequency: currencyFrequency
    };
}

// Enhanced file validation and upload
async function validateAndUploadFile(file) {
    if (!file) return;
    
    // Validate file type
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    if (!CONFIG.ALLOWED_TYPES.includes(fileExtension)) {
        showNotification(`Please upload a CSV or PDF file. Received: ${fileExtension}`, 'error');
        return;
    }
    
    // Validate file size
    if (file.size > CONFIG.MAX_FILE_SIZE) {
        const sizeMB = (file.size / (1024 * 1024)).toFixed(1);
        const maxSizeMB = (CONFIG.MAX_FILE_SIZE / (1024 * 1024)).toFixed(0);
        showNotification(`File size (${sizeMB}MB) exceeds maximum allowed size (${maxSizeMB}MB)`, 'error');
        return;
    }
    
    // Check for empty file
    if (file.size === 0) {
        showNotification('File appears to be empty', 'error');
        return;
    }
    
    handleFileUpload(file);
}

// Utility function to show notifications
function showNotification(message, type) {
    showAlert(message, type);
}

// Utility function to update progress
function updateProgress(stage) {
    const progressBar = document.querySelector('.progress-bar');
    if (!progressBar) return;
    
    let progress = 0;
    let label = 'Processing...';
    
    switch (stage) {
        case 'upload':
            progress = 25;
            label = 'Uploading...';
            break;
        case 'process':
            progress = 50;
            label = 'Processing...';
            break;
        case 'analyze':
            progress = 75;
            label = 'Analyzing...';
            break;
        case 'completed':
            progress = 100;
            label = 'Complete!';
            break;
    }
    
    progressBar.style.width = `${progress}%`;
    progressBar.setAttribute('aria-valuenow', progress);
    
    const labelElement = progressBar.querySelector('.progress-label');
    if (labelElement) {
        labelElement.textContent = label;
    }
}

// Enhanced currency formatting with support for multiple currencies
const CURRENCY_INFO = {
    'USD': { symbol: '$', position: 'before', decimal: 2, locale: 'en-US' },
    'INR': { symbol: '₹', position: 'before', decimal: 2, locale: 'en-IN' },
    'EUR': { symbol: '€', position: 'after', decimal: 2, locale: 'de-DE' },
    'GBP': { symbol: '£', position: 'before', decimal: 2, locale: 'en-GB' },
    'JPY': { symbol: '¥', position: 'before', decimal: 0, locale: 'ja-JP' },
    'CAD': { symbol: 'C$', position: 'before', decimal: 2, locale: 'en-CA' },
    'AUD': { symbol: 'A$', position: 'before', decimal: 2, locale: 'en-AU' },
    'CHF': { symbol: 'CHF', position: 'after', decimal: 2, locale: 'de-CH' },
    'CNY': { symbol: '¥', position: 'before', decimal: 2, locale: 'zh-CN' },
    'SEK': { symbol: 'kr', position: 'after', decimal: 2, locale: 'sv-SE' },
    'NOK': { symbol: 'kr', position: 'after', decimal: 2, locale: 'nb-NO' },
    'DKK': { symbol: 'kr', position: 'after', decimal: 2, locale: 'da-DK' },
    'PLN': { symbol: 'zł', position: 'after', decimal: 2, locale: 'pl-PL' },
    'CZK': { symbol: 'Kč', position: 'after', decimal: 2, locale: 'cs-CZ' },
    'HUF': { symbol: 'Ft', position: 'after', decimal: 0, locale: 'hu-HU' },
    'RUB': { symbol: '₽', position: 'after', decimal: 2, locale: 'ru-RU' },
    'BRL': { symbol: 'R$', position: 'before', decimal: 2, locale: 'pt-BR' },
    'MXN': { symbol: '$', position: 'before', decimal: 2, locale: 'es-MX' },
    'ZAR': { symbol: 'R', position: 'before', decimal: 2, locale: 'en-ZA' },
    'KRW': { symbol: '₩', position: 'before', decimal: 0, locale: 'ko-KR' },
    'SGD': { symbol: 'S$', position: 'before', decimal: 2, locale: 'en-SG' },
    'HKD': { symbol: 'HK$', position: 'before', decimal: 2, locale: 'en-HK' },
    'NZD': { symbol: 'NZ$', position: 'before', decimal: 2, locale: 'en-NZ' },
    'THB': { symbol: '฿', position: 'before', decimal: 2, locale: 'th-TH' },
    'MYR': { symbol: 'RM', position: 'before', decimal: 2, locale: 'ms-MY' },
    'IDR': { symbol: 'Rp', position: 'before', decimal: 0, locale: 'id-ID' },
    'PHP': { symbol: '₱', position: 'before', decimal: 2, locale: 'en-PH' }
};

function formatCurrency(amount, currency = 'USD', options = {}) {
    if (amount === null || amount === undefined || isNaN(amount)) {
        return 'N/A';
    }
    
    const { showSign = true } = options;
    const sign = showSign && amount !== 0 ? (amount > 0 ? '+' : '') : '';
    
    const currencyInfo = CURRENCY_INFO[currency] || CURRENCY_INFO['USD'];
    
    try {
        // Try to use Intl.NumberFormat for proper formatting
        const formatted = new Intl.NumberFormat(currencyInfo.locale, {
            style: 'decimal',
            minimumFractionDigits: currencyInfo.decimal,
            maximumFractionDigits: currencyInfo.decimal
        }).format(Math.abs(amount));
        
        // Add currency symbol
        if (currencyInfo.position === 'before') {
            return `${sign}${currencyInfo.symbol}${formatted}`;
        } else {
            return `${sign}${formatted} ${currencyInfo.symbol}`;
        }
    } catch (error) {
        // Fallback formatting
        const formatted = Math.abs(amount).toFixed(currencyInfo.decimal);
        if (currencyInfo.position === 'before') {
            return `${sign}${currencyInfo.symbol}${formatted}`;
        } else {
            return `${sign}${formatted} ${currencyInfo.symbol}`;
        }
    }
}

// Utility function to get date range
function getDateRange(transactions) {
    if (!transactions || transactions.length === 0) {
        return { start: new Date(), end: new Date() };
    }
    
    const dates = transactions.map(t => new Date(t.date)).filter(d => !isNaN(d));
    return {
        start: new Date(Math.min(...dates)),
        end: new Date(Math.max(...dates))
    };
}

// Utility function to refresh transactions
async function refreshTransactions() {
    // This function can be expanded to reload transactions from server if needed
    console.log('Refreshing transactions...');
}

// Utility function to show file stats
function showFileStats(stats) {
    if (!stats) return;
    
    const statsHtml = `
        <div class="file-stats mt-3">
            <h6><i class="fas fa-info-circle me-2"></i>File Statistics</h6>
            <div class="row text-center">
                <div class="col-md-3">
                    <div class="stat-item">
                        <div class="stat-number">${stats.total_transactions}</div>
                        <div class="stat-label">Transactions</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-item">
                        <div class="stat-number">${stats.categories}</div>
                        <div class="stat-label">Categories</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-item">
                        <div class="stat-number">${stats.date_range?.start || 'N/A'}</div>
                        <div class="stat-label">From</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-item">
                        <div class="stat-number">${stats.date_range?.end || 'N/A'}</div>
                        <div class="stat-label">To</div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    const uploadSection = document.querySelector('.upload-section');
    if (uploadSection) {
        const existingStats = uploadSection.querySelector('.file-stats');
        if (existingStats) {
            existingStats.remove();
        }
        uploadSection.insertAdjacentHTML('beforeend', statsHtml);
    }
}

// Handle file upload with enhanced progress tracking
async function handleFileUpload(file) {
    if (isLoading) {
        showNotification('Another operation is in progress. Please wait.', 'warning');
        return;
    }
    
    isLoading = true;
    updateProgress('upload');
    showLoading(true);  // Show loading indicator
    
    const uploadProgress = document.getElementById('uploadProgress');
    const progressBar = uploadProgress.querySelector('.progress-bar');
    uploadProgress.style.display = 'block';
    progressBar.style.width = '0%';
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Upload failed');
        }
        
        const data = await response.json();
        
        // Success case
        if (data.success) {
            currentTransactions = data.transactions;
            sessionId = data.session_id || sessionId;
            
            // Store primary currency for global use
            if (data.primary_currency) {
                window.primaryCurrency = data.primary_currency;
            }
            
            if (data.status) {
                updateProgress(data.status.stage);
                showNotification(data.status.message, 'info');
            }
            
            showNotification(
                `Successfully processed ${data.transactions.length} transactions in ${data.processing_time}s!`,
                'success'
            );

            if (data.stats) {
                showFileStats(data.stats);
            }

            // Show results section
            const resultsSection = document.getElementById('resultsSection');
            if (resultsSection) {
                resultsSection.style.display = 'block';
            }
            
            updateProgress('analyze');
            await processResults();
            
            await refreshTransactions(); // Refresh the transaction list
        } else {
            // Handle other types of responses
            if (data.warning) {
                showNotification(data.warning, 'warning');
            }
            if (data.redirect) {
                window.location.href = data.redirect;
            }
        }
        
    } catch (error) {
        console.error('Upload error:', error);
        
        let errorMessage = 'Error uploading file. Please try again.';
        if (error.name === 'AbortError') {
            errorMessage = 'Upload timed out. Please try with a smaller file.';
        } else if (error.message.includes('413')) {
            errorMessage = 'File too large. Maximum size is 16MB.';
        } else if (error.message.includes('400')) {
            errorMessage = 'Invalid file format or corrupted file.';
        }
        
        showNotification(errorMessage, 'error');
        updateProgress('upload');
        
    } finally {
        isLoading = false;
        showLoading(false);
        uploadProgress.style.display = 'none';
    }
}

// Process results and display them
async function processResults(currencyAnalysis = null) {
    try {
        console.log('Processing results for', currentTransactions.length, 'transactions');  // Debug log
        
        // Show loading state
        showNotification('Analyzing transactions...', 'info');
        
        // If no currency analysis provided, create one
        if (!currencyAnalysis) {
            currencyAnalysis = analyzeTransactionsByCurrency(currentTransactions);
        }
        
        // Analyze transactions
        const analysisResponse = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ transactions: currentTransactions })
        });

        if (!analysisResponse.ok) {
            const errorText = await analysisResponse.text();
            console.error('Analysis failed:', analysisResponse.status, errorText);
            throw new Error(`Analysis failed: ${analysisResponse.status} ${errorText}`);
        }

        const analysisResult = await analysisResponse.json();
        console.log('Analysis result:', analysisResult);  // Debug log
        
        if (analysisResult.success) {
            currentAnalysis = analysisResult.spending_analysis;
            currentRecommendations = analysisResult.budget_recommendations;
            
            // Generate charts
            await generateCharts();
            
            // Display results
            displaySummaryStats();
            displayBudgetRecommendations();
            displayTransactionsTable();
            
            // Show results section
            document.getElementById('resultsSection').style.display = 'block';
            
            // Scroll to results
            document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
        }
    } catch (error) {
        console.error('Analysis error:', error);
        showAlert('Error analyzing transactions', 'danger');
    }
}

// Generate charts
async function generateCharts() {
    try {
        const chartsResponse = await fetch('/charts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ transactions: currentTransactions })
        });

        const chartsResult = await chartsResponse.json();
        
        if (chartsResult.success) {
            const charts = chartsResult.charts;
            
            // Monthly spending chart
            if (charts.monthly_spending && charts.monthly_spending.data) {
                Plotly.newPlot('monthlyChart', charts.monthly_spending.data, charts.monthly_spending.layout);
            } else {
                console.log('Monthly chart data missing:', charts.monthly_spending);
            }
            
            // Category breakdown chart
            if (charts.category_breakdown && charts.category_breakdown.data) {
                Plotly.newPlot('categoryChart', charts.category_breakdown.data, charts.category_breakdown.layout);
            } else {
                console.log('Category chart data missing:', charts.category_breakdown);
            }
            
            // Daily pattern chart
            if (charts.daily_pattern && charts.daily_pattern.data) {
                Plotly.newPlot('dailyChart', charts.daily_pattern.data, charts.daily_pattern.layout);
            } else {
                console.log('Daily pattern chart data missing:', charts.daily_pattern);
            }
            
            // Budget vs actual chart
            if (charts.budget_vs_actual && charts.budget_vs_actual.data) {
                Plotly.newPlot('budgetChart', charts.budget_vs_actual.data, charts.budget_vs_actual.layout);
            } else {
                console.log('Budget chart data missing:', charts.budget_vs_actual);
            }
        } else {
            console.error('Charts response not successful:', chartsResult);
        }
    } catch (error) {
        console.error('Charts error:', error);
        showAlert('Error generating charts: ' + error.message, 'danger');
    }
}

// Display summary statistics
function displaySummaryStats() {
    const statsContainer = document.getElementById('summaryStats');
    
    if (!currentAnalysis || Object.keys(currentAnalysis).length === 0) {
        statsContainer.innerHTML = '<div class="col-12"><p class="text-muted">No data available</p></div>';
        return;
    }
    
    // Get primary currency from analysis or global variable
    const primaryCurrency = currentAnalysis.currency || window.primaryCurrency || 'USD';
    
    // Create stats using primary currency
    let stats = [];
    
    if (currentAnalysis.total_expenses) {
        stats.push({
            label: 'Total Expenses',
            value: formatCurrency(currentAnalysis.total_expenses, primaryCurrency),
            icon: 'fas fa-dollar-sign'
        });
        
        stats.push({
            label: 'Transactions',
            value: currentAnalysis.total_transactions,
            icon: 'fas fa-receipt'
        });
        
        if (currentAnalysis.avg_daily_expense) {
            stats.push({
                label: 'Avg Daily',
                value: formatCurrency(currentAnalysis.avg_daily_expense, primaryCurrency),
                icon: 'fas fa-calendar-day'
            });
        }
        
        // Show currency information
        stats.push({
            label: 'Currency',
            value: primaryCurrency,
            icon: 'fas fa-coins'
        });
    }
    
    stats.push({
        label: 'Analysis Period',
        value: `${currentAnalysis.analysis_period?.days || '0'} days`,
        icon: 'fas fa-clock'
    });

    statsContainer.innerHTML = stats.map(stat => `
        <div class="col-md-3 col-sm-6">
            <div class="stats-card text-center">
                <div class="stats-number">${stat.value}</div>
                <div class="stats-label">
                    <i class="${stat.icon} me-2"></i>${stat.label}
                </div>
            </div>
        </div>
    `).join('');
}

// Display budget recommendations
function displayBudgetRecommendations() {
    const container = document.getElementById('budgetRecommendations');
    
    if (!currentRecommendations || Object.keys(currentRecommendations).length === 0) {
        container.innerHTML = '<p class="text-muted">No recommendations available</p>';
        return;
    }

    let html = '';
    
    // Get primary currency
    const primaryCurrency = currentAnalysis.currency || window.primaryCurrency || 'USD';
    
    // Monthly income
    if (currentRecommendations.monthly_income) {
        const formattedIncome = formatCurrency(
            currentRecommendations.monthly_income, 
            primaryCurrency,
            { showSign: false }
        );
        html += `
            <div class="alert alert-info alert-custom">
                <h6><i class="fas fa-info-circle me-2"></i>Monthly Income</h6>
                <p class="mb-0">Your estimated monthly income is <strong>${formattedIncome}</strong></p>
            </div>
        `;
    }

    // Alerts
    if (currentRecommendations.alerts && currentRecommendations.alerts.length > 0) {
        currentRecommendations.alerts.forEach(alert => {
            const alertClass = alert.severity === 'high' ? 'danger' : 'warning';
            html += `
                <div class="alert alert-${alertClass} alert-custom">
                    <h6><i class="fas fa-exclamation-triangle me-2"></i>${alert.category.charAt(0).toUpperCase() + alert.category.slice(1)}</h6>
                    <p class="mb-0">${alert.message}</p>
                </div>
            `;
        });
    }

    // Budget recommendations by category
    if (currentRecommendations.recommended_budgets) {
        html += '<h6 class="mt-4 mb-3">Category Budget Recommendations</h6>';
        html += '<div class="row">';
        
        Object.entries(currentRecommendations.recommended_budgets).forEach(([category, data]) => {
            const statusClass = data.difference >= 0 ? 'success' : 'danger';
            const statusIcon = data.difference >= 0 ? 'check-circle' : 'exclamation-circle';
            
            html += `
                <div class="col-md-6 mb-3">
                    <div class="card">
                        <div class="card-body">
                            <h6 class="card-title text-capitalize">${category}</h6>
                            <div class="row">
                                <div class="col-6">
                                    <small class="text-muted">Recommended</small>
                                    <div class="fw-bold">${formatCurrency(data.recommended, primaryCurrency, { showSign: false })}</div>
                                </div>
                                <div class="col-6">
                                    <small class="text-muted">Current</small>
                                    <div class="fw-bold">${formatCurrency(data.current, primaryCurrency, { showSign: false })}</div>
                                </div>
                            </div>
                            <div class="mt-2">
                                <span class="badge bg-${statusClass}">
                                    <i class="fas fa-${statusIcon} me-1"></i>
                                    ${data.difference >= 0 ? 'Under Budget' : 'Over Budget'}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
    }

    container.innerHTML = html;
}

// Display transactions table
function displayTransactionsTable() {
    console.log('Displaying transactions table');  // Debug log
    
    const tbody = document.getElementById('transactionsBody');
    if (!tbody) {
        console.error('Transaction table body not found');
        return;
    }
    
    if (!currentTransactions || currentTransactions.length === 0) {
        console.log('No transactions to display');  // Debug log
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No transactions found</td></tr>';
        return;
    }
    
    // Group transactions by currency
    const currencyAnalysis = analyzeTransactionsByCurrency(currentTransactions);
    console.log(`Displaying ${currentTransactions.length} transactions in ${currencyAnalysis.groups.size} currencies`);  // Debug log
    
    // Sort transactions by date (most recent first)
    const sortedTransactions = [...currentTransactions].sort((a, b) => 
        new Date(b.date) - new Date(a.date)
    );

    tbody.innerHTML = sortedTransactions.map(transaction => `
        <tr class="currency-${transaction.currency || 'USD'}">
            <td>${formatDate(transaction.date)}</td>
            <td>${transaction.description}</td>
            <td class="${transaction.amount >= 0 ? 'text-success' : 'text-danger'} amount-cell">
                ${formatCurrency(transaction.amount, transaction.currency || 'USD')}
            </td>
            <td>
                <span class="category-badge text-capitalize">${transaction.category}</span>
            </td>
            <td>
                <span class="badge bg-${transaction.type === 'credit' ? 'success' : 'danger'}">
                    ${transaction.type}
                </span>
            </td>
        </tr>
    `).join('');
}

// Export data to CSV
async function exportData() {
    if (!currentTransactions || currentTransactions.length === 0) {
        showAlert('No data to export', 'warning');
        return;
    }

    try {
        const response = await fetch('/export', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ transactions: currentTransactions })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'transactions.csv';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showAlert('Data exported successfully!', 'success');
        } else {
            showAlert('Error exporting data', 'danger');
        }
    } catch (error) {
        console.error('Export error:', error);
        showAlert('Error exporting data', 'danger');
    }
}

// Utility functions
function showLoading(show) {
    const loading = document.getElementById('loading');
    const uploadArea = document.getElementById('uploadArea');
    
    if (show) {
        loading.style.display = 'block';
        uploadArea.style.display = 'none';
    } else {
        loading.style.display = 'none';
        uploadArea.style.display = 'block';
    }
}

function showAlert(message, type) {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert');
    existingAlerts.forEach(alert => alert.remove());

    // Create new alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-custom alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    // Insert at the top of the main container
    const mainContainer = document.querySelector('.main-container');
    mainContainer.insertBefore(alertDiv, mainContainer.firstChild);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('Financial Tracker initialized');
    
    // Get session ID from body data attribute
    const sessionIdElement = document.body.getAttribute('data-session-id');
    if (sessionIdElement) {
        sessionId = sessionIdElement;
    }
    
    // Set up file input handling
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('uploadArea');
    
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            if (e.target.files && e.target.files[0]) {
                validateAndUploadFile(e.target.files[0]);
            }
        });
    }
    
    // Set up drag and drop
    if (uploadArea) {
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                validateAndUploadFile(e.dataTransfer.files[0]);
            }
        });
        
        // Click to upload
        uploadArea.addEventListener('click', function(e) {
            if (fileInput && e.target === uploadArea) {
                fileInput.click();
            }
        });
    }
    
    // Set up form submission
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            if (fileInput.files && fileInput.files[0]) {
                validateAndUploadFile(fileInput.files[0]);
            }
        });
    }
});
