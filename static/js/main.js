// Global variables
let currentInvoiceId = null;
let editItemModal = null;
let gstSlabChart = null;
let taxDistributionChart = null;

// DOM Ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize Bootstrap components
    editItemModal = new bootstrap.Modal(document.getElementById('edit-item-modal'));
    
    // Set up navigation
    setupNavigation();
    
    // Set up event listeners
    setupEventListeners();
    
    // Load initial data
    loadInvoices();
    
    // Load dashboard data
    loadDashboardData();
});

// Navigation setup
function setupNavigation() {
    const navLinks = {
        'upload-nav': 'upload-page',
        'history-nav': 'history-page',
        'dashboard-nav': 'dashboard-page'
    };
    
    Object.entries(navLinks).forEach(([navId, pageId]) => {
        document.getElementById(navId).addEventListener('click', (e) => {
            e.preventDefault();
            
            // Hide all pages
            document.querySelectorAll('.content-page').forEach(page => {
                page.classList.add('d-none');
            });
            
            // Remove active class from all nav links
            document.querySelectorAll('.nav-link').forEach(link => {
                link.classList.remove('active');
            });
            
            // Show selected page
            document.getElementById(pageId).classList.remove('d-none');
            
            // Add active class to clicked nav link
            e.target.classList.add('active');
        });
    });
    
    // Set upload page as default active page
    document.getElementById('upload-nav').classList.add('active');
}

// Set up event listeners
function setupEventListeners() {
    // File input change
    document.getElementById('invoice-file').addEventListener('change', handleFileSelect);
    
    // Form submissions
    document.getElementById('upload-form').addEventListener('submit', handleFormSubmit);
    document.getElementById('edit-item-form').addEventListener('submit', (e) => e.preventDefault());
    document.getElementById('gstr1-form').addEventListener('submit', handleGSTR1Submit);
    
    // Button clicks
    document.getElementById('save-item-btn').addEventListener('click', saveItemChanges);
    document.getElementById('pdf-report-btn').addEventListener('click', () => generateReport('pdf'));
    document.getElementById('json-report-btn').addEventListener('click', () => generateReport('json'));
    document.getElementById('history-pdf-btn').addEventListener('click', () => generateHistoryReport('pdf'));
    document.getElementById('history-json-btn').addEventListener('click', () => generateHistoryReport('json'));
    document.getElementById('back-to-list-btn').addEventListener('click', () => {
        document.getElementById('invoices-list').classList.remove('d-none');
        document.getElementById('invoice-details').classList.add('d-none');
    });
}

// Handle file selection
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    // Clear previous previews
    document.getElementById('image-preview').classList.add('d-none');
    document.getElementById('pdf-preview').classList.add('d-none');
    
    // Show appropriate preview
    if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('image-preview');
            preview.src = e.target.result;
            preview.classList.remove('d-none');
        }
        reader.readAsDataURL(file);
    } else if (file.type === 'application/pdf') {
        document.getElementById('pdf-preview').classList.remove('d-none');
    }
}

// Handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('invoice-file');
    if (!fileInput.files[0]) {
        showAlert('Please select a file to upload', 'danger');
        return;
    }
    
    // Create form data
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    // Show loading state
    showAlert('Processing invoice, please wait...', 'info');
    
    try {
        const response = await fetch('/api/process-invoice', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to process invoice');
        }
        
        // Hide loading notification
        clearAlerts();
        
        // Show success
        showAlert('Invoice processed successfully!', 'success');
        
        // Update global variable
        currentInvoiceId = data.invoice_id;
        
        // Display results
        displayInvoiceResults(data);
        
    } catch (error) {
        showAlert(`Error: ${error.message}`, 'danger');
    }
}

// Display invoice processing results
function displayInvoiceResults(data) {
    // Show results area
    document.getElementById('results-area').classList.remove('d-none');
    
    // Clear tables
    document.querySelector('#items-table tbody').innerHTML = '';
    document.querySelector('#gst-summary-table tbody').innerHTML = '';
    
    // Add items to table
    data.items.forEach((item, index) => {
        const row = document.createElement('tr');
        row.dataset.itemId = item.id || '';
        row.dataset.index = index;
        
        row.innerHTML = `
            <td>${item.item}</td>
            <td>${item.qty}</td>
            <td>₹${item.unit_price.toFixed(2)}</td>
            <td>₹${item.total.toFixed(2)}</td>
            <td>${item.gst_rate}%</td>
            <td>${item.hsn_code || '-'}</td>
            <td>
                <button class="btn btn-sm btn-primary edit-item-btn">
                    <i class="fas fa-edit"></i>
                </button>
            </td>
        `;
        
        document.querySelector('#items-table tbody').appendChild(row);
        
        // Add edit button event listener
        row.querySelector('.edit-item-btn').addEventListener('click', () => {
            openEditItemModal(item);
        });
    });
    
    // Add GST breakdown to table
    let totalTaxable = 0;
    let totalTax = 0;
    
    Object.entries(data.gst_breakdown).forEach(([rate, amounts]) => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>${rate}%</td>
            <td>₹${amounts.taxable_amount.toFixed(2)}</td>
            <td>₹${amounts.tax_amount.toFixed(2)}</td>
        `;
        
        document.querySelector('#gst-summary-table tbody').appendChild(row);
        
        totalTaxable += amounts.taxable_amount;
        totalTax += amounts.tax_amount;
    });
    
    // Update totals
    document.getElementById('total-taxable').textContent = `₹${totalTaxable.toFixed(2)}`;
    document.getElementById('total-tax').textContent = `₹${totalTax.toFixed(2)}`;
}

// Open edit item modal
function openEditItemModal(item) {
    document.getElementById('edit-item-id').value = item.id || '';
    document.getElementById('edit-item-name').value = item.item;
    document.getElementById('edit-item-qty').value = item.qty;
    document.getElementById('edit-item-price').value = item.unit_price;
    document.getElementById('edit-item-gst').value = item.gst_rate;
    document.getElementById('edit-item-hsn').value = item.hsn_code || '';
    
    editItemModal.show();
}

// Save item changes
async function saveItemChanges() {
    const itemId = document.getElementById('edit-item-id').value;
    const itemName = document.getElementById('edit-item-name').value;
    const qty = parseFloat(document.getElementById('edit-item-qty').value);
    const unitPrice = parseFloat(document.getElementById('edit-item-price').value);
    const gstRate = parseFloat(document.getElementById('edit-item-gst').value);
    const hsnCode = document.getElementById('edit-item-hsn').value;
    
    // Calculate total
    const total = qty * unitPrice;
    
    // Create item data
    const itemData = {
        id: itemId,
        item: itemName,
        qty: qty,
        unit_price: unitPrice,
        total: total,
        gst_rate: gstRate,
        hsn_code: hsnCode
    };
    
    try {
        const response = await fetch('/api/update-item', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(itemData)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to update item');
        }
        
        // Close modal
        editItemModal.hide();
        
        // Show success
        showAlert('Item updated successfully!', 'success');
        
        // Reload current invoice data for the upload page
        if (currentInvoiceId) {
            await loadInvoiceDetails(currentInvoiceId, true);
        }
        
    } catch (error) {
        showAlert(`Error: ${error.message}`, 'danger');
    }
}

// Generate report for current invoice
function generateReport(type) {
    if (!currentInvoiceId) {
        showAlert('No invoice selected', 'warning');
        return;
    }
    
    const url = `/api/reports/${type}/${currentInvoiceId}`;
    window.open(url, '_blank');
}

// Generate report for invoice in history
function generateHistoryReport(type) {
    const invoiceId = document.getElementById('invoice-info').dataset.invoiceId;
    
    if (!invoiceId) {
        showAlert('No invoice selected', 'warning');
        return;
    }
    
    const url = `/api/reports/${type}/${invoiceId}`;
    window.open(url, '_blank');
}

// Handle GSTR1 form submission
async function handleGSTR1Submit(e) {
    e.preventDefault();
    
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;
    
    if (!startDate || !endDate) {
        showAlert('Please select both start and end dates', 'warning');
        return;
    }
    
    // Create data for request
    const data = {
        start_date: startDate,
        end_date: endDate
    };
    
    try {
        const response = await fetch('/api/reports/gstr1', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to generate GSTR-1 report');
        }
        
        // Create blob and download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `GSTR1_report_${startDate}_to_${endDate}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        // Show success
        showAlert('GSTR-1 report generated successfully!', 'success');
        
    } catch (error) {
        showAlert(`Error: ${error.message}`, 'danger');
    }
}

// Load invoices for history page
async function loadInvoices() {
    try {
        const response = await fetch('/api/invoices');
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to load invoices');
        }
        
        // Clear table
        document.querySelector('#invoices-table tbody').innerHTML = '';
        
        if (data.length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = '<td colspan="4" class="text-center">No invoices found. Upload your first invoice to get started!</td>';
            document.querySelector('#invoices-table tbody').appendChild(row);
            return;
        }
        
        // Add invoices to table
        data.forEach(invoice => {
            const row = document.createElement('tr');
            const date = new Date(invoice.created_at).toLocaleDateString();
            
            row.innerHTML = `
                <td>${invoice.id.substring(0, 8)}...</td>
                <td>${invoice.file_name}</td>
                <td>${date}</td>
                <td>
                    <button class="btn btn-sm btn-primary view-invoice-btn" data-id="${invoice.id}">
                        <i class="fas fa-eye"></i> View
                    </button>
                </td>
            `;
            
            document.querySelector('#invoices-table tbody').appendChild(row);
            
            // Add view button event listener
            row.querySelector('.view-invoice-btn').addEventListener('click', (e) => {
                const invoiceId = e.target.closest('button').dataset.id;
                loadInvoiceDetails(invoiceId);
            });
        });
        
    } catch (error) {
        showAlert(`Error loading invoices: ${error.message}`, 'danger');
    }
}

// Load invoice details
async function loadInvoiceDetails(invoiceId, isUploadPage = false) {
    try {
        const response = await fetch(`/api/invoice/${invoiceId}`);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to load invoice details');
        }
        
        const invoice = data.invoice;
        const items = data.items;
        
        if (isUploadPage) {
            // For upload page, just update the current invoice data
            currentInvoiceId = invoiceId;
            
            const gstBreakdown = calculateGSTBreakdown(items);
            
            // Display on upload page
            const displayData = {
                invoice_id: invoiceId,
                items: items,
                gst_breakdown: gstBreakdown
            };
            
            displayInvoiceResults(displayData);
            return;
        }
        
        // Show invoice details section
        document.getElementById('invoices-list').classList.add('d-none');
        document.getElementById('invoice-details').classList.remove('d-none');
        
        // Format date
        const date = new Date(invoice.created_at).toLocaleDateString();
        
        // Display invoice info
        const invoiceInfo = document.getElementById('invoice-info');
        invoiceInfo.dataset.invoiceId = invoiceId;
        invoiceInfo.innerHTML = `
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">${invoice.file_name}</h5>
                    <p class="card-text">
                        <strong>Date:</strong> ${date}<br>
                        <strong>Invoice ID:</strong> ${invoice.id}<br>
                        <strong>File Type:</strong> ${invoice.file_type}
                    </p>
                </div>
            </div>
        `;
        
        // Clear tables
        document.querySelector('#history-items-table tbody').innerHTML = '';
        document.querySelector('#history-gst-table tbody').innerHTML = '';
        
        // Add items to table
        items.forEach(item => {
            const row = document.createElement('tr');
            
            row.innerHTML = `
                <td>${item.item}</td>
                <td>${item.qty}</td>
                <td>₹${item.unit_price.toFixed(2)}</td>
                <td>₹${item.total.toFixed(2)}</td>
                <td>${item.gst_rate}%</td>
                <td>${item.hsn_code || '-'}</td>
            `;
            
            document.querySelector('#history-items-table tbody').appendChild(row);
        });
        
        // Calculate and display GST breakdown
        const gstBreakdown = calculateGSTBreakdown(items);
        let totalTaxable = 0;
        let totalTax = 0;
        
        Object.entries(gstBreakdown).forEach(([rate, amounts]) => {
            const row = document.createElement('tr');
            
            row.innerHTML = `
                <td>${rate}%</td>
                <td>₹${amounts.taxable_amount.toFixed(2)}</td>
                <td>₹${amounts.tax_amount.toFixed(2)}</td>
            `;
            
            document.querySelector('#history-gst-table tbody').appendChild(row);
            
            totalTaxable += amounts.taxable_amount;
            totalTax += amounts.tax_amount;
        });
        
        // Update totals
        document.getElementById('history-total-taxable').textContent = `₹${totalTaxable.toFixed(2)}`;
        document.getElementById('history-total-tax').textContent = `₹${totalTax.toFixed(2)}`;
        
    } catch (error) {
        showAlert(`Error loading invoice details: ${error.message}`, 'danger');
    }
}

// Calculate GST breakdown from items
function calculateGSTBreakdown(items) {
    const breakdown = {};
    
    items.forEach(item => {
        const gstRate = item.gst_rate || 0;
        if (!breakdown[gstRate]) {
            breakdown[gstRate] = {
                taxable_amount: 0,
                tax_amount: 0
            };
        }
        
        const taxableAmount = item.total || 0;
        const taxAmount = taxableAmount * (gstRate / 100);
        
        breakdown[gstRate].taxable_amount += taxableAmount;
        breakdown[gstRate].tax_amount += taxAmount;
    });
    
    return breakdown;
}

// Load dashboard data
async function loadDashboardData() {
    try {
        const response = await fetch('/api/gst-statistics');
        const data = await response.json();
        
        if (!response.ok) {
            // Just silently fail for dashboard, as it's not critical
            return;
        }
        
        // Update statistics
        document.getElementById('dashboard-total-tax').textContent = `₹${data.total_tax.toFixed(2)}`;
        document.getElementById('dashboard-total-taxable').textContent = `₹${data.total_taxable.toFixed(2)}`;
        
        // Get all invoices to count
        const invoicesResponse = await fetch('/api/invoices');
        const invoicesData = await invoicesResponse.json();
        
        if (invoicesResponse.ok) {
            document.getElementById('dashboard-total-invoices').textContent = invoicesData.length;
        }
        
        // Create charts
        createGSTCharts(data.tax_by_slab);
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// Create GST charts
function createGSTCharts(taxBySlabData) {
    // Extract data for charts
    const labels = Object.keys(taxBySlabData).map(rate => `${rate}%`);
    const taxAmounts = Object.values(taxBySlabData).map(data => data.tax_amount);
    const taxableAmounts = Object.values(taxBySlabData).map(data => data.taxable_amount);
    
    // Colors for charts
    const backgroundColors = [
        'rgba(54, 162, 235, 0.7)',
        'rgba(255, 99, 132, 0.7)',
        'rgba(255, 206, 86, 0.7)',
        'rgba(75, 192, 192, 0.7)',
        'rgba(153, 102, 255, 0.7)'
    ];
    
    // Create or update GST by slab chart
    const gstSlabCtx = document.getElementById('gst-by-slab-chart').getContext('2d');
    
    if (gstSlabChart) {
        gstSlabChart.destroy();
    }
    
    gstSlabChart = new Chart(gstSlabCtx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Tax Amount (₹)',
                data: taxAmounts,
                backgroundColor: backgroundColors,
                borderColor: backgroundColors.map(color => color.replace('0.7', '1')),
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            responsive: true,
            maintainAspectRatio: true
        }
    });
    
    // Create or update tax distribution chart
    const taxDistCtx = document.getElementById('tax-distribution-chart').getContext('2d');
    
    if (taxDistributionChart) {
        taxDistributionChart.destroy();
    }
    
    taxDistributionChart = new Chart(taxDistCtx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                label: 'Tax Distribution',
                data: taxAmounts,
                backgroundColor: backgroundColors,
                borderColor: backgroundColors.map(color => color.replace('0.7', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true
        }
    });
}

// Show alert
function showAlert(message, type) {
    const alertArea = document.getElementById('alert-area');
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    alertArea.innerHTML = alertHtml;
}

// Clear all alerts
function clearAlerts() {
    document.getElementById('alert-area').innerHTML = '';
}
