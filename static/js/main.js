// Main JavaScript file for TaxLyzer application

document.addEventListener('DOMContentLoaded', function() {
    // Setup navigation
    setupNavigation();
    
    // Setup event listeners
    setupEventListeners();
    
    // Initialize file drag and drop
    initializeFileDragDrop();
});

// Set up navigation between pages
function setupNavigation() {
    const navigationLinks = {
        'chat-button': 'chatbot-page',
        'upload-nav': 'upload-page',
        'history-nav': 'history-page',
        'dashboard-nav': 'dashboard-page',
        'trends-nav': 'trends-page'
    };
    
    // Handle navigation clicks
    Object.keys(navigationLinks).forEach(navId => {
        const navElement = document.getElementById(navId);
        if (navElement) {
            navElement.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Hide home and all content pages
                document.getElementById('home-page').classList.add('d-none');
                document.getElementById('magic-section').classList.add('d-none');
                
                document.querySelectorAll('.content-page').forEach(page => {
                    page.classList.add('d-none');
                });
                
                // Show selected page
                document.getElementById(navigationLinks[navId]).classList.remove('d-none');
                
                // Update active nav link
                document.querySelectorAll('.nav-link').forEach(link => {
                    link.classList.remove('active');
                });
                this.classList.add('active');
                
                // Load data for specific pages
                if (navId === 'history-nav') {
                    loadInvoices();
                } else if (navId === 'dashboard-nav') {
                    loadDashboardData();
                } else if (navId === 'trends-nav') {
                    loadTrendAnalysis();
                    loadTopHSNCodes();
                    loadGSTSlabDistribution();
                }
            });
        }
    });
    
    // Handle "Try Now" button
    const tryNowBtn = document.getElementById('try-now-btn');
    if (tryNowBtn) {
        tryNowBtn.addEventListener('click', function() {
            // Hide home page
            document.getElementById('home-page').classList.add('d-none');
            document.getElementById('magic-section').classList.add('d-none');
            
            // Show upload page
            document.querySelectorAll('.content-page').forEach(page => {
                page.classList.add('d-none');
            });
            document.getElementById('upload-page').classList.remove('d-none');
            
            // Update active nav
            document.querySelectorAll('.nav-link').forEach(link => {
                link.classList.remove('active');
            });
            document.getElementById('upload-nav').classList.add('active');
        });
    }
}

// Initialize file drag and drop functionality
function initializeFileDragDrop() {
    const dropArea = document.getElementById('drop-area');
    
    if (dropArea) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
        });
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, unhighlight, false);
        });
        
        dropArea.addEventListener('drop', handleDrop, false);
    }
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    function highlight() {
        dropArea.classList.add('highlight');
    }
    
    function unhighlight() {
        dropArea.classList.remove('highlight');
    }
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            const fileInput = document.getElementById('landing-invoice-file');
            if (fileInput) {
                fileInput.files = files;
                
                // Trigger change event
                const event = new Event('change');
                fileInput.dispatchEvent(event);
            }
        }
    }
}

// Set up all event listeners
function setupEventListeners() {
    // File inputs
    const landingFileInput = document.getElementById('landing-invoice-file');
    if (landingFileInput) {
        landingFileInput.addEventListener('change', handleLandingFileSelect);
    }
    
    const fileInput = document.getElementById('invoice-file');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }
    
    // Form submissions
    const landingUploadForm = document.getElementById('landing-upload-form');
    if (landingUploadForm) {
        landingUploadForm.addEventListener('submit', handleLandingFormSubmit);
    }
    
    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleFormSubmit);
    }
    
    // Report generation
    const pdfReportBtn = document.getElementById('pdf-report-btn');
    if (pdfReportBtn) {
        pdfReportBtn.addEventListener('click', function() {
            generateReport('pdf');
        });
    }
    
    const jsonReportBtn = document.getElementById('json-report-btn');
    if (jsonReportBtn) {
        jsonReportBtn.addEventListener('click', function() {
            generateReport('json');
        });
    }
    
    const historyPdfBtn = document.getElementById('history-pdf-btn');
    if (historyPdfBtn) {
        historyPdfBtn.addEventListener('click', function() {
            generateHistoryReport('pdf');
        });
    }
    
    const historyJsonBtn = document.getElementById('history-json-btn');
    if (historyJsonBtn) {
        historyJsonBtn.addEventListener('click', function() {
            generateHistoryReport('json');
        });
    }
    
    // Back to list button
    const backToListBtn = document.getElementById('back-to-list-btn');
    if (backToListBtn) {
        backToListBtn.addEventListener('click', function() {
            document.getElementById('invoices-list').classList.remove('d-none');
            document.getElementById('invoice-details').classList.add('d-none');
        });
    }
    
    // Save item changes button
    const saveItemBtn = document.getElementById('save-item-btn');
    if (saveItemBtn) {
        saveItemBtn.addEventListener('click', saveItemChanges);
    }
    
    // GSTR-1 Report form
    const gstr1Form = document.getElementById('gstr1-form');
    if (gstr1Form) {
        gstr1Form.addEventListener('submit', handleGSTR1Submit);
    }
    
    // Trend filters 
    const applyTrendFilters = document.getElementById('apply-trend-filters');
    if (applyTrendFilters) {
        applyTrendFilters.addEventListener('click', function() {
            loadTrendAnalysis();
            loadTopHSNCodes();
            loadGSTSlabDistribution();
        });
    }
}

// Trend analysis functions
function loadTrendAnalysis() {
    const startDate = document.getElementById('trend-start-date')?.value || '';
    const endDate = document.getElementById('trend-end-date')?.value || '';
    const groupBy = document.getElementById('trend-group-by')?.value || 'month';
    
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    params.append('group_by', groupBy);
    
    fetch(`/api/trend-analysis?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showAlert(data.error, 'danger');
                return;
            }
            
            createTrendChart(data.time_series, groupBy);
            updateTrendSummary(data.summary);
        })
        .catch(error => {
            console.error('Error loading trend analysis:', error);
            showAlert('Failed to load trend analysis data', 'danger');
        });
}

function loadTopHSNCodes() {
    const startDate = document.getElementById('trend-start-date')?.value || '';
    const endDate = document.getElementById('trend-end-date')?.value || '';
    
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    params.append('limit', '10');
    
    fetch(`/api/top-hsn-codes?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showAlert(data.error, 'danger');
                return;
            }
            
            createTopHSNChart(data);
            
            // Update HSN table
            const table = document.getElementById('top-hsn-table');
            if (table) {
                const tbody = table.querySelector('tbody');
                tbody.innerHTML = '';
                
                data.forEach(hsn => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${hsn.hsn_code}</td>
                        <td>${hsn.description || ''}</td>
                        <td>${hsn.count}</td>
                        <td>₹${hsn.total_tax.toFixed(2)}</td>
                    `;
                    tbody.appendChild(row);
                });
            }
        })
        .catch(error => {
            console.error('Error loading top HSN codes:', error);
            showAlert('Failed to load HSN code data', 'danger');
        });
}

function loadGSTSlabDistribution() {
    const startDate = document.getElementById('trend-start-date')?.value || '';
    const endDate = document.getElementById('trend-end-date')?.value || '';
    
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    fetch(`/api/slab-distribution?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showAlert(data.error, 'danger');
                return;
            }
            
            createSlabDistributionChart(data);
        })
        .catch(error => {
            console.error('Error loading GST slab distribution:', error);
            showAlert('Failed to load GST slab distribution data', 'danger');
        });
}

function createTrendChart(timeSeriesData, groupBy) {
    const ctx = document.getElementById('trend-chart');
    if (!ctx) return;
    
    // Destroy existing chart if any
    if (window.trendChart) {
        window.trendChart.destroy();
    }
    
    const labels = timeSeriesData.map(item => item.period);
    const taxData = timeSeriesData.map(item => item.total_tax);
    const taxableData = timeSeriesData.map(item => item.total_taxable);
    
    window.trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Total Tax (₹)',
                    data: taxData,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1,
                    yAxisID: 'y'
                },
                {
                    label: 'Taxable Amount (₹)',
                    data: taxableData,
                    borderColor: 'rgb(255, 99, 132)',
                    tension: 0.1,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Tax Amount (₹)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Taxable Amount (₹)'
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: getTimeLabel(groupBy)
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += '₹' + context.parsed.y.toFixed(2);
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
}

function getTimeLabel(groupBy) {
    switch (groupBy) {
        case 'day': return 'Day';
        case 'week': return 'Week';
        case 'month': return 'Month';
        case 'quarter': return 'Quarter';
        default: return 'Time Period';
    }
}

function createTopHSNChart(hsnData) {
    const ctx = document.getElementById('top-hsn-chart');
    if (!ctx) return;
    
    // Destroy existing chart if any
    if (window.hsnChart) {
        window.hsnChart.destroy();
    }
    
    const labels = hsnData.map(item => item.hsn_code);
    const taxData = hsnData.map(item => item.total_tax);
    
    window.hsnChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Tax Amount (₹)',
                data: taxData,
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgb(54, 162, 235)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Tax Amount (₹)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'HSN Code'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        title: function(tooltipItems) {
                            const idx = tooltipItems[0].dataIndex;
                            const hsn = hsnData[idx];
                            return `HSN: ${hsn.hsn_code} ${hsn.description ? `(${hsn.description})` : ''}`;
                        },
                        label: function(context) {
                            const idx = context.dataIndex;
                            const hsn = hsnData[idx];
                            let label = `Tax Amount: ₹${hsn.total_tax.toFixed(2)}`;
                            return label;
                        },
                        afterLabel: function(context) {
                            const idx = context.dataIndex;
                            const hsn = hsnData[idx];
                            return [
                                `Taxable Amount: ₹${hsn.total_amount.toFixed(2)}`,
                                `GST Rate: ${hsn.gst_rate}%`,
                                `Count: ${hsn.count} items`
                            ];
                        }
                    }
                }
            }
        }
    });
}

function createSlabDistributionChart(slabData) {
    const ctx = document.getElementById('slab-distribution-chart');
    if (!ctx) return;
    
    // Destroy existing chart if any
    if (window.slabChart) {
        window.slabChart.destroy();
    }
    
    const labels = slabData.map(item => `${item.slab}%`);
    const countData = slabData.map(item => item.count);
    const taxData = slabData.map(item => item.total_tax);
    
    window.slabChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                label: 'GST Slabs',
                data: countData,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.5)',
                    'rgba(54, 162, 235, 0.5)',
                    'rgba(255, 206, 86, 0.5)',
                    'rgba(75, 192, 192, 0.5)',
                    'rgba(153, 102, 255, 0.5)'
                ],
                borderColor: [
                    'rgb(255, 99, 132)',
                    'rgb(54, 162, 235)',
                    'rgb(255, 206, 86)',
                    'rgb(75, 192, 192)',
                    'rgb(153, 102, 255)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const idx = context.dataIndex;
                            const slab = slabData[idx];
                            return [
                                `${slab.slab}% GST: ${slab.count} items`,
                                `Tax Amount: ₹${slab.total_tax.toFixed(2)}`,
                                `Taxable Amount: ₹${slab.total_amount.toFixed(2)}`
                            ];
                        }
                    }
                }
            }
        }
    });
}

function updateTrendSummary(summary) {
    if (!summary) return;
    
    // Update summary cards
    const elements = {
        'trend-total-gst': summary.total_tax ? `₹${summary.total_tax.toFixed(2)}` : '₹0.00',
        'trend-growth-rate': summary.growth_rate ? `${summary.growth_rate.toFixed(2)}%` : '0%',
        'trend-avg-monthly': summary.avg_monthly ? `₹${summary.avg_monthly.toFixed(2)}` : '₹0.00',
        'trend-projected': summary.projected_annual ? `₹${summary.projected_annual.toFixed(2)}` : '₹0.00'
    };
    
    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    });
}

// Helper function to show alerts
function showAlert(message, type = 'success') {
    const alertArea = document.getElementById('alert-area');
    if (!alertArea) return;
    
    // Clear existing alerts
    clearAlerts();
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertArea.appendChild(alertDiv);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.classList.remove('show');
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.parentNode.removeChild(alertDiv);
                }
            }, 150);
        }
    }, 5000);
}

// Helper function to clear all alerts
function clearAlerts() {
    const alertArea = document.getElementById('alert-area');
    if (alertArea) {
        alertArea.innerHTML = '';
    }
}
