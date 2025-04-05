$(document).ready(function() {
    // Global chart instances
    let gstSlabChart = null;
    let taxDistributionChart = null;
    
    // Initialize file drag & drop
    initializeFileDragDrop();
    
    // Set up navigation tabs
    setupNavigation();
    
// Set up navigation between tabs
function setupNavigation() {
    const tabs = document.querySelectorAll('.navbar-nav .nav-link');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get target section id
            let targetId;
            
            if (this.id === 'upload-nav') {
                targetId = 'upload-section';
            } else if (this.id === 'history-nav') {
                targetId = 'history-section';
            } else if (this.id === 'dashboard-nav') {
                targetId = 'dashboard-section';
            } else if (this.id === 'trends-nav') {
                targetId = 'trends-section';
            }
            
            // Hide all sections
            document.querySelectorAll('.container[id$="-section"]').forEach(section => {
                section.classList.add('d-none');
            });
            
            // Show target section
            if (targetId) {
                document.getElementById(targetId).classList.remove('d-none');
            }
            
            // Update active tab
            tabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Load section data if needed
            if (targetId === 'dashboard-section') {
                loadDashboardData();
            } else if (targetId === 'history-section') {
                loadInvoices();
            } else if (targetId === 'trends-section') {
                // Initialize trend analysis if it's present
                const trendStartDate = document.getElementById('trend-start-date');
                const trendEndDate = document.getElementById('trend-end-date');
                
                if (trendStartDate && trendEndDate) {
                    // Set default dates if not already set
                    if (!trendStartDate.value) {
                        // Set to 3 months ago
                        const threeMonthsAgo = new Date();
                        threeMonthsAgo.setMonth(threeMonthsAgo.getMonth() - 3);
                        trendStartDate.value = threeMonthsAgo.toISOString().split('T')[0];
                    }
                    
                    if (!trendEndDate.value) {
                        // Set to today
                        const today = new Date();
                        trendEndDate.value = today.toISOString().split('T')[0];
                    }
                    
                    // Load trend data
                    loadTrendAnalysis();
                }
            }
        });
    });
}
    // Set up event listeners
    setupEventListeners();
    
    // Load initial data
    if (window.location.pathname === '/' || window.location.pathname === '/index.html') {
        if (document.getElementById('dashboard-section')) {
            loadDashboardData();
        } else if (document.getElementById('history-section')) {
            loadInvoices();
        }
    }
});

// Initialize file drag and drop
function initializeFileDragDrop() {
    const dragDropAreas = document.querySelectorAll('.drag-drop-area');
    
    if (dragDropAreas.length === 0) return;
    
    dragDropAreas.forEach(dropArea => {
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
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    function highlight() {
        this.classList.add('drag-drop-highlight');
    }
    
    function unhighlight() {
        this.classList.remove('drag-drop-highlight');
    }
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            // Check if this is the main landing page drop area
            if (this.id === 'landing-drag-drop') {
                handleLandingFileSelect({ target: { files: files } });
            } else {
                handleFileSelect({ target: { files: files } });
            }
        }
    }
}

// Set up navigation between tabs
            
            // Show target section
            document.getElementById(targetId).classList.remove('d-none');
            
            // Update active tab
            tabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Load section data if needed
            if (targetId === 'dashboard-section') {
                loadDashboardData();
            } else if (targetId === 'history-section') {
                loadInvoices();
            } else if (targetId === 'trends-section') {
                // Initialize trend analysis if it's present
                const trendStartDate = document.getElementById('trend-start-date');
                const trendEndDate = document.getElementById('trend-end-date');
                
                if (trendStartDate && trendEndDate) {
                    // Set default dates if not already set
                    if (!trendStartDate.value) {
                        // Set to 3 months ago
                        const threeMonthsAgo = new Date();
                        threeMonthsAgo.setMonth(threeMonthsAgo.getMonth() - 3);
                        trendStartDate.value = threeMonthsAgo.toISOString().split('T')[0];
                    }
                    
                    if (!trendEndDate.value) {
                        // Set to today
                        const today = new Date();
                        trendEndDate.value = today.toISOString().split('T')[0];
                    }
                    
                    // Load trend data
                    loadTrendAnalysis();
                }
            }
        });
    });
}

// Set up navigation between tabs
function setupNavigation() {
    const tabs = document.querySelectorAll('.navbar-nav .nav-link');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get target section id
            let targetId;
            
            if (this.id === 'upload-nav') {
                targetId = 'upload-section';
            } else if (this.id === 'history-nav') {
                targetId = 'history-section';
            } else if (this.id === 'dashboard-nav') {
                targetId = 'dashboard-section';
            } else if (this.id === 'trends-nav') {
                targetId = 'trends-section';
            }
            
            // Hide all sections
            document.querySelectorAll('.container[id$="-section"]').forEach(section => {
                section.classList.add('d-none');
            });
            
            // Show target section
            if (targetId) {
                document.getElementById(targetId).classList.remove('d-none');
            }
            
            // Update active tab
            tabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Load section data if needed
            if (targetId === 'dashboard-section') {
                loadDashboardData();
            } else if (targetId === 'history-section') {
                loadInvoices();
            } else if (targetId === 'trends-section') {
                // Initialize trend analysis if it's present
                const trendStartDate = document.getElementById('trend-start-date');
                const trendEndDate = document.getElementById('trend-end-date');
                
                if (trendStartDate && trendEndDate) {
                    // Set default dates if not already set
                    if (!trendStartDate.value) {
                        // Set to 3 months ago
                        const threeMonthsAgo = new Date();
                        threeMonthsAgo.setMonth(threeMonthsAgo.getMonth() - 3);
                        trendStartDate.value = threeMonthsAgo.toISOString().split('T')[0];
                    }
                    
                    if (!trendEndDate.value) {
                        // Set to today
                        const today = new Date();
                        trendEndDate.value = today.toISOString().split('T')[0];
                    }
                    
                    // Load trend data
                    loadTrendAnalysis();
                }
            }
        });
    });
}
// Set up event listeners
function setupEventListeners() {
    // File upload form
    const fileUploadForm = document.getElementById('upload-form');
    if (fileUploadForm) {
        fileUploadForm.addEventListener('submit', handleFormSubmit);
    }
    
    // Landing page form
    const landingForm = document.getElementById('landing-upload-form');
    if (landingForm) {
        landingForm.addEventListener('submit', handleLandingFormSubmit);
    }
    
    // File input
    const fileInput = document.getElementById('invoice-file');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }
    
    // Landing page file input
    const landingFileInput = document.getElementById('landing-file-input');
    if (landingFileInput) {
        landingFileInput.addEventListener('change', handleLandingFileSelect);
    }
    
    // Batch upload file input
    const batchFileInput = document.getElementById('batch-files');
    
    // GSTR-1 form
    const gstr1Form = document.getElementById('gstr1-form');
    if (gstr1Form) {
        gstr1Form.addEventListener('submit', handleGSTR1Submit);
    }
    
    // Save item changes
    const saveItemButton = document.getElementById('save-item-changes');
    if (saveItemButton) {
        saveItemButton.addEventListener('click', saveItemChanges);
    }
    
    // Trend analysis form
    const trendForm = document.getElementById('trend-filter-form');
    if (trendForm) {
        trendForm.addEventListener('submit', function(e) {
            e.preventDefault();
            loadTrendAnalysis();
        });
    }
}

// Handle file selection
function handleFileSelect(e) {
    const fileInput = e.target;
    const fileLabel = document.getElementById('file-label');
    
    if (fileInput.files.length > 0) {
        fileLabel.textContent = fileInput.files[0].name;
    } else {
        fileLabel.textContent = 'Choose file';
    }
}

// Handle landing page file selection
function handleLandingFileSelect(e) {
    const fileInput = e.target;
    const landingFileLabel = document.getElementById('landing-file-label');
    const uploadButton = document.getElementById('landing-upload-button');
    
    if (fileInput.files.length > 0) {
        landingFileLabel.textContent = fileInput.files[0].name;
        uploadButton.removeAttribute('disabled');
    } else {
        landingFileLabel.textContent = 'Drop your invoice here or click to browse';
        uploadButton.setAttribute('disabled', 'disabled');
    }
}

// Handle landing page form submission
async function handleLandingFormSubmit(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('landing-file-input');
    const progressContainer = document.getElementById('upload-progress-container');
    const progressBar = document.getElementById('upload-progress-bar');
    
    if (fileInput.files.length === 0) {
        showAlert('Please select a file to upload', 'warning');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    try {
        // Show progress
        progressContainer.classList.remove('d-none');
        progressBar.style.width = '0%';
        progressBar.setAttribute('aria-valuenow', 0);
        
        // Simulate progress (since we don't have actual progress events)
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += 5;
            if (progress >= 90) {
                clearInterval(progressInterval);
            }
            progressBar.style.width = `${progress}%`;
            progressBar.setAttribute('aria-valuenow', progress);
        }, 100);
        
        // Make API call
        const response = await fetch('/api/process-invoice', {
            method: 'POST',
            body: formData
        });
        
        // Clear interval and set to 100%
        clearInterval(progressInterval);
        progressBar.style.width = '100%';
        progressBar.setAttribute('aria-valuenow', 100);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to process invoice');
        }
        
        const data = await response.json();
        
        // Switch to results view
        document.getElementById('landing-upload-container').classList.add('d-none');
        document.getElementById('landing-results-container').classList.remove('d-none');
        
        // Display results
        displayInvoiceResults(data);
        
    } catch (error) {
        showAlert(`Error: ${error.message}`, 'danger');
    } finally {
        // Hide progress after a short delay
        setTimeout(() => {
            progressContainer.classList.add('d-none');
        }, 500);
    }
}

// Handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('invoice-file');
    const progressContainer = document.getElementById('upload-progress-container');
    const progressBar = document.getElementById('upload-progress-bar');
    
    if (fileInput.files.length === 0) {
        showAlert('Please select a file to upload', 'warning');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    try {
        // Show progress
        progressContainer.classList.remove('d-none');
        progressBar.style.width = '0%';
        progressBar.setAttribute('aria-valuenow', 0);
        
        // Simulate progress (since we don't have actual progress events)
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += 5;
            if (progress >= 90) {
                clearInterval(progressInterval);
            }
            progressBar.style.width = `${progress}%`;
            progressBar.setAttribute('aria-valuenow', progress);
        }, 100);
        
        // Make API call
        const response = await fetch('/api/process-invoice', {
            method: 'POST',
            body: formData
        });
        
        // Clear interval and set to 100%
        clearInterval(progressInterval);
        progressBar.style.width = '100%';
        progressBar.setAttribute('aria-valuenow', 100);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to process invoice');
        }
        
        const data = await response.json();
        
        // Display results
        displayInvoiceResults(data);
        
        // Show success message
        showAlert('Invoice processed successfully!', 'success');
        
        // Reset form
        document.getElementById('upload-form').reset();
        document.getElementById('file-label').textContent = 'Choose file';
        
    } catch (error) {
        showAlert(`Error: ${error.message}`, 'danger');
    } finally {
        // Hide progress after a short delay
        setTimeout(() => {
            progressContainer.classList.add('d-none');
        }, 500);
    }
}

// Display invoice processing results
function displayInvoiceResults(data) {
    // Get result containers
    const itemsTableBody = document.getElementById('items-table-body') || 
                          document.getElementById('landing-items-table-body');
    const gstBreakdownTable = document.getElementById('gst-breakdown-table') || 
                             document.getElementById('landing-gst-breakdown-table');
    const invoiceIdElement = document.getElementById('invoice-id') || 
                            document.getElementById('landing-invoice-id');
    
    if (invoiceIdElement) {
        invoiceIdElement.textContent = data.invoice_id;
        
        // Set invoice ID in download buttons
        const pdfButton = document.getElementById('download-pdf-btn') || 
                         document.getElementById('landing-download-pdf-btn');
        const jsonButton = document.getElementById('download-json-btn') || 
                          document.getElementById('landing-download-json-btn');
        
        if (pdfButton) {
            pdfButton.setAttribute('data-invoice-id', data.invoice_id);
        }
        
        if (jsonButton) {
            jsonButton.setAttribute('data-invoice-id', data.invoice_id);
        }
    }
    
    // Populate items table
    if (itemsTableBody) {
        itemsTableBody.innerHTML = '';
        
        data.items.forEach((item, index) => {
            const row = document.createElement('tr');
            
            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${item.name || ''}</td>
                <td>${item.hsn_code || ''}</td>
                <td>${item.quantity || 1}</td>
                <td>${item.unit_price?.toFixed(2) || '0.00'}</td>
                <td>${item.total?.toFixed(2) || '0.00'}</td>
                <td>${item.gst_rate || 0}%</td>
                <td>₹${(item.total * (item.gst_rate / 100)).toFixed(2)}</td>
                <td>
                    <button class="btn btn-sm btn-primary edit-item-btn" 
                            data-item-id="${item.id}" 
                            data-bs-toggle="modal" 
                            data-bs-target="#editItemModal">
                        Edit
                    </button>
                </td>
            `;
            
            itemsTableBody.appendChild(row);
        });
        
        // Add event listeners to edit buttons
        document.querySelectorAll('.edit-item-btn').forEach(button => {
            button.addEventListener('click', function() {
                const itemId = this.getAttribute('data-item-id');
                const item = data.items.find(i => i.id === itemId);
                if (item) {
                    openEditItemModal(item);
                }
            });
        });
    }
    
    // Populate GST breakdown table
    if (gstBreakdownTable) {
        gstBreakdownTable.innerHTML = '';
        
        let totalTaxableAmount = 0;
        let totalTaxAmount = 0;
        
        Object.entries(data.gst_breakdown).forEach(([rate, amounts]) => {
            const row = document.createElement('tr');
            
            row.innerHTML = `
                <td>${rate}%</td>
                <td>₹${amounts.taxable_amount.toFixed(2)}</td>
                <td>₹${amounts.tax_amount.toFixed(2)}</td>
            `;
            
            gstBreakdownTable.appendChild(row);
            
            totalTaxableAmount += amounts.taxable_amount;
            totalTaxAmount += amounts.tax_amount;
        });
        
        // Add total row
        const totalRow = document.createElement('tr');
        totalRow.className = 'table-dark';
        
        totalRow.innerHTML = `
            <td><strong>Total</strong></td>
            <td><strong>₹${totalTaxableAmount.toFixed(2)}</strong></td>
            <td><strong>₹${totalTaxAmount.toFixed(2)}</strong></td>
        `;
        
        gstBreakdownTable.appendChild(totalRow);
    }
}

// Open edit item modal
function openEditItemModal(item) {
    document.getElementById('edit-item-id').value = item.id;
    document.getElementById('edit-item-name').value = item.name || '';
    document.getElementById('edit-item-hsn').value = item.hsn_code || '';
    document.getElementById('edit-item-quantity').value = item.quantity || 1;
    document.getElementById('edit-item-price').value = item.unit_price || 0;
    document.getElementById('edit-item-total').value = item.total || 0;
    document.getElementById('edit-item-gst').value = item.gst_rate || 0;
}

// Save item changes
async function saveItemChanges() {
    const itemId = document.getElementById('edit-item-id').value;
    const itemName = document.getElementById('edit-item-name').value;
    const itemHsn = document.getElementById('edit-item-hsn').value;
    const itemQuantity = parseFloat(document.getElementById('edit-item-quantity').value) || 1;
    const itemPrice = parseFloat(document.getElementById('edit-item-price').value) || 0;
    const itemTotal = parseFloat(document.getElementById('edit-item-total').value) || 0;
    const itemGst = parseFloat(document.getElementById('edit-item-gst').value) || 0;
    
    const updatedItem = {
        id: itemId,
        name: itemName,
        hsn_code: itemHsn,
        quantity: itemQuantity,
        unit_price: itemPrice,
        total: itemTotal,
        gst_rate: itemGst
    };
    
    try {
        const response = await fetch('/api/update-item', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updatedItem)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to update item');
        }
        
        // Get the invoice ID
        const invoiceIdElement = document.getElementById('invoice-id') || 
                               document.getElementById('landing-invoice-id');
        const invoiceId = invoiceIdElement?.textContent;
        
        // Close modal
        const modalElement = document.getElementById('editItemModal');
        const modal = bootstrap.Modal.getInstance(modalElement);
        modal.hide();
        
        // Show success message
        showAlert('Item updated successfully!', 'success');
        
        // Reload invoice details
        if (invoiceId) {
            const isUploadPage = Boolean(document.getElementById('landing-invoice-id'));
            await loadInvoiceDetails(invoiceId, isUploadPage);
        }
        
    } catch (error) {
        showAlert(`Error: ${error.message}`, 'danger');
    }
}

// Generate report
function generateReport(type) {
    const invoiceId = document.getElementById('invoice-id')?.textContent || 
                     document.getElementById('landing-invoice-id')?.textContent;
    
    if (!invoiceId) {
        showAlert('Invoice ID not found', 'warning');
        return;
    }
    
    const url = `/api/reports/${type}/${invoiceId}`;
    window.open(url, '_blank');
}

// Generate report from history
function generateHistoryReport(type) {
    const button = event.target.closest('button');
    const invoiceId = button.getAttribute('data-invoice-id');
    
    if (!invoiceId) {
        showAlert('Invoice ID not found', 'warning');
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

// Load invoices for history section
async function loadInvoices() {
    try {
        const response = await fetch('/api/invoices');
        
        if (!response.ok) {
            throw new Error('Failed to load invoices');
        }
        
        const invoices = await response.json();
        const invoicesTableBody = document.getElementById('invoices-table-body');
        
        if (!invoicesTableBody) return;
        
        invoicesTableBody.innerHTML = '';
        
        if (invoices.length === 0) {
            const emptyRow = document.createElement('tr');
            emptyRow.innerHTML = `
                <td colspan="5" class="text-center">No invoices found</td>
            `;
            invoicesTableBody.appendChild(emptyRow);
            return;
        }
        
        // Sort invoices by created_at (newest first)
        invoices.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        
        invoices.forEach(invoice => {
            const row = document.createElement('tr');
            const createdAt = new Date(invoice.created_at);
            
            row.innerHTML = `
                <td>${invoice.id}</td>
                <td>${invoice.file_name}</td>
                <td>${createdAt.toLocaleString()}</td>
                <td>
                    <button class="btn btn-sm btn-primary view-invoice-btn"
                            data-invoice-id="${invoice.id}">
                        View
                    </button>
                </td>
                <td>
                    <div class="dropdown">
                        <button class="btn btn-sm btn-secondary dropdown-toggle" 
                                type="button" 
                                data-bs-toggle="dropdown" 
                                aria-expanded="false">
                            Export
                        </button>
                        <ul class="dropdown-menu">
                            <li>
                                <button class="dropdown-item" 
                                        onclick="generateHistoryReport('pdf')" 
                                        data-invoice-id="${invoice.id}">
                                    PDF
                                </button>
                            </li>
                            <li>
                                <button class="dropdown-item" 
                                        onclick="generateHistoryReport('json')" 
                                        data-invoice-id="${invoice.id}">
                                    JSON
                                </button>
                            </li>
                        </ul>
                    </div>
                </td>
            `;
            
            invoicesTableBody.appendChild(row);
        });
        
        // Add event listeners to view buttons
        document.querySelectorAll('.view-invoice-btn').forEach(button => {
            button.addEventListener('click', function() {
                const invoiceId = this.getAttribute('data-invoice-id');
                loadInvoiceDetails(invoiceId);
            });
        });
        
    } catch (error) {
        console.error('Error loading invoices:', error);
    }
}

// Load invoice details
async function loadInvoiceDetails(invoiceId, isUploadPage = false) {
    try {
        const response = await fetch(`/api/invoice/${invoiceId}`);
        
        if (!response.ok) {
            throw new Error('Failed to load invoice details');
        }
        
        const data = await response.json();
        
        // Set prefix based on page
        const prefix = isUploadPage ? 'landing-' : '';
        
        // Set invoice ID
        const invoiceIdElement = document.getElementById(`${prefix}invoice-id`);
        if (invoiceIdElement) {
            invoiceIdElement.textContent = invoiceId;
        }
        
        // Update download buttons
        const pdfButton = document.getElementById(`${prefix}download-pdf-btn`);
        const jsonButton = document.getElementById(`${prefix}download-json-btn`);
        
        if (pdfButton) {
            pdfButton.setAttribute('data-invoice-id', invoiceId);
        }
        
        if (jsonButton) {
            jsonButton.setAttribute('data-invoice-id', invoiceId);
        }
        
        // Populate items table
        const itemsTableBody = document.getElementById(`${prefix}items-table-body`);
        if (itemsTableBody) {
            itemsTableBody.innerHTML = '';
            
            data.items.forEach((item, index) => {
                const row = document.createElement('tr');
                
                row.innerHTML = `
                    <td>${index + 1}</td>
                    <td>${item.name || ''}</td>
                    <td>${item.hsn_code || ''}</td>
                    <td>${item.quantity || 1}</td>
                    <td>${item.unit_price?.toFixed(2) || '0.00'}</td>
                    <td>${item.total?.toFixed(2) || '0.00'}</td>
                    <td>${item.gst_rate || 0}%</td>
                    <td>₹${(item.total * (item.gst_rate / 100)).toFixed(2)}</td>
                    <td>
                        <button class="btn btn-sm btn-primary edit-item-btn" 
                                data-item-id="${item.id}" 
                                data-bs-toggle="modal" 
                                data-bs-target="#editItemModal">
                            Edit
                        </button>
                    </td>
                `;
                
                itemsTableBody.appendChild(row);
            });
            
            // Add event listeners to edit buttons
            document.querySelectorAll('.edit-item-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const itemId = this.getAttribute('data-item-id');
                    const item = data.items.find(i => i.id === itemId);
                    if (item) {
                        openEditItemModal(item);
                    }
                });
            });
        }
        
        // Calculate GST breakdown
        const gstBreakdown = calculateGSTBreakdown(data.items);
        
        // Populate GST breakdown table
        const gstBreakdownTable = document.getElementById(`${prefix}gst-breakdown-table`);
        if (gstBreakdownTable) {
            gstBreakdownTable.innerHTML = '';
            
            let totalTaxableAmount = 0;
            let totalTaxAmount = 0;
            
            Object.entries(gstBreakdown).forEach(([rate, amounts]) => {
                const row = document.createElement('tr');
                
                row.innerHTML = `
                    <td>${rate}%</td>
                    <td>₹${amounts.taxable_amount.toFixed(2)}</td>
                    <td>₹${amounts.tax_amount.toFixed(2)}</td>
                `;
                
                gstBreakdownTable.appendChild(row);
                
                totalTaxableAmount += amounts.taxable_amount;
                totalTaxAmount += amounts.tax_amount;
            });
            
            // Add total row
            const totalRow = document.createElement('tr');
            totalRow.className = 'table-dark';
            
            totalRow.innerHTML = `
                <td><strong>Total</strong></td>
                <td><strong>₹${totalTaxableAmount.toFixed(2)}</strong></td>
                <td><strong>₹${totalTaxAmount.toFixed(2)}</strong></td>
            `;
            
            gstBreakdownTable.appendChild(totalRow);
        }
        
        // If on history page, update summary
        if (!isUploadPage) {
            const createdAt = new Date(data.invoice.created_at);
            document.getElementById('history-invoice-date').textContent = createdAt.toLocaleString();
            document.getElementById('history-file-name').textContent = data.invoice.file_name;
            
            // Calculate totals
            let totalTaxable = 0;
            let totalTax = 0;
            
            data.items.forEach(item => {
                totalTaxable += item.total || 0;
                totalTax += (item.total || 0) * ((item.gst_rate || 0) / 100);
            });
            
            document.getElementById('history-total-taxable').textContent = `₹${totalTaxable.toFixed(2)}`;
            document.getElementById('history-total-tax').textContent = `₹${totalTax.toFixed(2)}`;
        }
        
    } catch (error) {
        console.error('Error loading invoice details:', error);
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
        
        if (!response.ok) {
            // Just silently fail for dashboard, as it's not critical
            console.error('Error loading dashboard data');
            return;
        }
        
        const data = await response.json();
        
        // Update statistics
        const totalTaxElement = document.getElementById('dashboard-total-tax');
        const totalTaxableElement = document.getElementById('dashboard-total-taxable');
        
        if (totalTaxElement) {
            totalTaxElement.textContent = `₹${data.total_tax.toFixed(2)}`;
        }
        
        if (totalTaxableElement) {
            totalTaxableElement.textContent = `₹${data.total_taxable.toFixed(2)}`;
        }
        
        // Get all invoices to count
        const invoicesResponse = await fetch('/api/invoices');
        
        if (invoicesResponse.ok) {
            const invoicesData = await invoicesResponse.json();
            const totalInvoicesElement = document.getElementById('dashboard-total-invoices');
            
            if (totalInvoicesElement) {
                totalInvoicesElement.textContent = invoicesData.length;
            }
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
    const gstSlabCtx = document.getElementById('gst-by-slab-chart')?.getContext('2d');
    
    if (gstSlabCtx) {
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
    }
    
    // Create or update tax distribution chart
    const taxDistCtx = document.getElementById('tax-distribution-chart')?.getContext('2d');
    
    if (taxDistCtx) {
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
}

// Load trend analysis data and create trend charts
let trendChart = null;
let topHSNChart = null;
let slabDistributionTrendChart = null;

async function loadTrendAnalysis() {
    try {
        // Get filter parameters
        const startDate = document.getElementById('trend-start-date')?.value;
        const endDate = document.getElementById('trend-end-date')?.value;
        const groupBy = document.getElementById('trend-group-by')?.value || 'month';
        
        // Fetch trend data
        const queryParams = new URLSearchParams();
        if (startDate) queryParams.append('start_date', startDate);
        if (endDate) queryParams.append('end_date', endDate);
        queryParams.append('group_by', groupBy);
        
        const response = await fetch(`/api/trends/analysis?${queryParams.toString()}`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to load trend analysis');
        }
        
        const data = await response.json();
        
        // Update summary statistics
        updateTrendSummary(data.summary);
        
        // Create trend chart
        createTrendChart(data.time_series, groupBy);
        
        // Load additional trend data
        loadTopHSNCodes();
        loadGSTSlabDistribution();
        
    } catch (error) {
        console.error('Error loading trend analysis:', error);
        showAlert(`Error loading trend analysis: ${error.message}`, 'danger');
    }
}

function updateTrendSummary(summary) {
    // Update summary elements
    const elements = {
        'trend-total-tax': summary.total_tax,
        'trend-total-taxable': summary.total_taxable,
        'trend-invoice-count': summary.invoice_count,
        'trend-item-count': summary.item_count,
        'trend-avg-tax': summary.avg_tax_per_invoice,
        'trend-avg-items': summary.avg_items_per_invoice
    };
    
    // Update each element if it exists
    for (const [id, value] of Object.entries(elements)) {
        const element = document.getElementById(id);
        if (element) {
            // Format currency values
            if (id.includes('tax') || id.includes('taxable')) {
                element.textContent = `₹${parseFloat(value || 0).toFixed(2)}`;
            } 
            // Format averages with 1 decimal place
            else if (id.includes('avg')) {
                element.textContent = parseFloat(value || 0).toFixed(1);
            }
            // Integer values
            else {
                element.textContent = value || 0;
            }
        }
    }
}

function createTrendChart(timeSeriesData, groupBy) {
    // Get chart context
    const ctx = document.getElementById('trend-chart')?.getContext('2d');
    if (!ctx) return;
    
    // Destroy existing chart
    if (trendChart) {
        trendChart.destroy();
    }
    
    // No data
    if (!timeSeriesData || timeSeriesData.length === 0) {
        // Create empty chart with message
        trendChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['No Data'],
                datasets: [{
                    label: 'Tax Amount',
                    data: [0],
                    backgroundColor: 'rgba(54, 162, 235, 0.7)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'No trend data available for the selected period'
                    }
                }
            }
        });
        return;
    }
    
    // Prepare data
    const labels = timeSeriesData.map(item => item.period);
    const taxData = timeSeriesData.map(item => item.tax_amount);
    const taxableData = timeSeriesData.map(item => item.taxable_amount);
    const invoiceCountData = timeSeriesData.map(item => item.invoice_count);
    
    // Create chart
    trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Tax Amount (₹)',
                    data: taxData,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    yAxisID: 'y',
                    fill: true
                },
                {
                    label: 'Invoice Count',
                    data: invoiceCountData,
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    yAxisID: 'y1',
                    type: 'bar'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
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
                    grid: {
                        drawOnChartArea: false
                    },
                    title: {
                        display: true,
                        text: 'Invoice Count'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: `GST Trend Analysis by ${groupBy.charAt(0).toUpperCase() + groupBy.slice(1)}`
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            }
        }
    });
}

async function loadTopHSNCodes() {
    try {
        // Get filter parameters
        const startDate = document.getElementById('trend-start-date')?.value;
        const endDate = document.getElementById('trend-end-date')?.value;
        const limit = 10; // Top 10 HSN codes
        
        // Fetch data
        const queryParams = new URLSearchParams();
        if (startDate) queryParams.append('start_date', startDate);
        if (endDate) queryParams.append('end_date', endDate);
        queryParams.append('limit', limit);
        
        const response = await fetch(`/api/trends/top-hsn?${queryParams.toString()}`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to load top HSN codes');
        }
        
        const data = await response.json();
        
        // Create chart
        createTopHSNChart(data.top_hsn_codes);
        
    } catch (error) {
        console.error('Error loading top HSN codes:', error);
    }
}

function createTopHSNChart(hsnData) {
    // Get chart context
    const ctx = document.getElementById('top-hsn-chart')?.getContext('2d');
    if (!ctx) return;
    
    // Destroy existing chart
    if (topHSNChart) {
        topHSNChart.destroy();
    }
    
    // No data
    if (!hsnData || hsnData.length === 0) {
        // Create empty chart with message
        topHSNChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['No Data'],
                datasets: [{
                    label: 'Count',
                    data: [0],
                    backgroundColor: 'rgba(75, 192, 192, 0.7)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'No HSN code data available'
                    }
                }
            }
        });
        return;
    }
    
    // Prepare data
    const labels = hsnData.map(item => item.hsn_code);
    const counts = hsnData.map(item => item.count);
    const taxAmounts = hsnData.map(item => item.tax_amount);
    
    // Create chart
    topHSNChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Frequency',
                    data: counts,
                    backgroundColor: 'rgba(75, 192, 192, 0.7)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1,
                    yAxisID: 'y'
                },
                {
                    label: 'Tax Amount (₹)',
                    data: taxAmounts,
                    backgroundColor: 'rgba(153, 102, 255, 0.7)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    borderWidth: 1,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Frequency'
                    },
                    beginAtZero: true
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Tax Amount (₹)'
                    },
                    beginAtZero: true,
                    grid: {
                        drawOnChartArea: false
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Top HSN Codes by Frequency'
                },
                tooltip: {
                    callbacks: {
                        afterLabel: function(context) {
                            const item = hsnData[context.dataIndex];
                            return `GST Rate: ${item.gst_rate}%`;
                        }
                    }
                }
            }
        }
    });
}

async function loadGSTSlabDistribution() {
    try {
        // Get filter parameters
        const startDate = document.getElementById('trend-start-date')?.value;
        const endDate = document.getElementById('trend-end-date')?.value;
        
        // Fetch data
        const queryParams = new URLSearchParams();
        if (startDate) queryParams.append('start_date', startDate);
        if (endDate) queryParams.append('end_date', endDate);
        
        const response = await fetch(`/api/trends/slab-distribution?${queryParams.toString()}`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to load GST slab distribution');
        }
        
        const data = await response.json();
        
        // Create chart
        createSlabDistributionChart(data.slab_distribution);
        
    } catch (error) {
        console.error('Error loading GST slab distribution:', error);
    }
}

function createSlabDistributionChart(slabData) {
    // Get chart context
    const ctx = document.getElementById('slab-distribution-chart')?.getContext('2d');
    if (!ctx) return;
    
    // Destroy existing chart
    if (slabDistributionTrendChart) {
        slabDistributionTrendChart.destroy();
    }
    
    // No data
    if (!slabData || Object.keys(slabData).length === 0) {
        // Create empty chart with message
        slabDistributionTrendChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['No Data'],
                datasets: [{
                    label: 'GST Slab Distribution',
                    data: [1],
                    backgroundColor: ['rgba(200, 200, 200, 0.7)']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'No GST slab data available'
                    }
                }
            }
        });
        return;
    }
    
    // Prepare data
    const labels = Object.keys(slabData).map(rate => `${rate}%`);
    const counts = Object.values(slabData).map(data => data.item_count);
    const taxAmounts = Object.values(slabData).map(data => data.tax_amount);
    
    // Colors for chart
    const backgroundColors = [
        'rgba(54, 162, 235, 0.7)',
        'rgba(255, 99, 132, 0.7)',
        'rgba(255, 206, 86, 0.7)',
        'rgba(75, 192, 192, 0.7)',
        'rgba(153, 102, 255, 0.7)',
        'rgba(255, 159, 64, 0.7)',
        'rgba(201, 203, 207, 0.7)'
    ];
    
    // Create chart
    slabDistributionTrendChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                label: 'Tax Amount',
                data: taxAmounts,
                backgroundColor: backgroundColors.slice(0, labels.length),
                borderColor: backgroundColors.map(color => color.replace('0.7', '1')).slice(0, labels.length),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                title: {
                    display: true,
                    text: 'GST Slab Distribution'
                },
                tooltip: {
                    callbacks: {
                        afterLabel: function(context) {
                            const slabKey = Object.keys(slabData)[context.dataIndex];
                            const item = slabData[slabKey];
                            return [
                                `Items: ${item.item_count}`,
                                `Taxable Amount: ₹${item.taxable_amount.toFixed(2)}`
                            ];
                        }
                    }
                }
            }
        }
    });
}

// Show alert
function showAlert(message, type) {
    const alertArea = document.getElementById('alert-area');
    if (!alertArea) return;
    
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
    const alertArea = document.getElementById('alert-area');
    if (alertArea) {
        alertArea.innerHTML = '';
    }
}
// Trend Analysis Functions
async function loadTrendAnalysis() {
    try {
        clearAlerts();
        
        const startDate = document.getElementById('trend-start-date').value;
        const endDate = document.getElementById('trend-end-date').value;
        const groupBy = document.getElementById('trend-group-by').value;
        
        // Show loading
        showAlert("Loading trend analysis data...", "info");
        
        // Get trend data from API
        const response = await fetch(`/api/trend-analysis?start_date=${startDate}&end_date=${endDate}&group_by=${groupBy}`);
        
        if (!response.ok) {
            throw new Error(`Failed to load trend data: ${response.statusText}`);
        }
        
        const trendData = await response.json();
        
        // Update summary statistics
        updateTrendSummary(trendData.summary);
        
        // Create time series chart
        createTrendChart(trendData.time_series, groupBy);
        
        // Clear loading alert
        clearAlerts();
        
        // Load additional charts
        loadTopHSNCodes();
        loadGSTSlabDistribution();
        
    } catch (error) {
        console.error("Error loading trend analysis:", error);
        showAlert(`Error loading trend analysis: ${error.message}`, "danger");
    }
}

function updateTrendSummary(summary) {
    // Update the summary cards with data
    document.getElementById('trend-total-tax').textContent = `₹${parseFloat(summary.total_tax).toFixed(2)}`;
    document.getElementById('trend-total-taxable').textContent = `₹${parseFloat(summary.total_taxable_value).toFixed(2)}`;
    document.getElementById('trend-invoice-count').textContent = summary.invoice_count;
    document.getElementById('trend-item-count').textContent = summary.item_count;
    document.getElementById('trend-avg-tax').textContent = `₹${parseFloat(summary.avg_tax_per_invoice).toFixed(2)}`;
    document.getElementById('trend-avg-items').textContent = parseFloat(summary.avg_items_per_invoice).toFixed(1);
}

function createTrendChart(timeSeriesData, groupBy) {
    // Get the canvas element
    const ctx = document.getElementById('trend-chart').getContext('2d');
    
    // Prepare data for Chart.js
    const labels = timeSeriesData.map(item => item.period);
    const taxData = timeSeriesData.map(item => item.total_tax);
    const taxableData = timeSeriesData.map(item => item.total_taxable_value);
    const invoiceCountData = timeSeriesData.map(item => item.invoice_count);
    
    // Destroy existing chart if it exists
    if (window.trendChart) {
        window.trendChart.destroy();
    }
    
    // Create a new chart
    window.trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Total Tax (₹)',
                    data: taxData,
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1
                },
                {
                    label: 'Total Taxable Value (₹)',
                    data: taxableData,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1
                },
                {
                    label: 'Invoice Count',
                    data: invoiceCountData,
                    borderColor: 'rgba(255, 159, 64, 1)',
                    backgroundColor: 'rgba(255, 159, 64, 0.2)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Amount (₹)'
                    }
                },
                y1: {
                    beginAtZero: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Invoice Count'
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
                title: {
                    display: true,
                    text: 'Tax and Invoice Trends Over Time'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
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
        default: return 'Period';
    }
}

async function loadTopHSNCodes() {
    try {
        // Get top HSN codes from API
        const response = await fetch('/api/top-hsn-codes');
        
        if (!response.ok) {
            throw new Error(`Failed to load HSN data: ${response.statusText}`);
        }
        
        const hsnData = await response.json();
        
        // Create the chart
        createTopHSNChart(hsnData);
        
    } catch (error) {
        console.error("Error loading HSN codes:", error);
    }
}

function createTopHSNChart(hsnData) {
    // Get the canvas element
    const ctx = document.getElementById('top-hsn-chart').getContext('2d');
    
    // Prepare data for Chart.js
    const labels = hsnData.map(item => `${item.hsn_code} (${item.description.substring(0, 15)}...)`);
    const counts = hsnData.map(item => item.count);
    const amounts = hsnData.map(item => item.total_amount);
    
    // Color palette
    const backgroundColors = [
        'rgba(54, 162, 235, 0.7)',
        'rgba(75, 192, 192, 0.7)',
        'rgba(153, 102, 255, 0.7)',
        'rgba(255, 159, 64, 0.7)',
        'rgba(255, 99, 132, 0.7)',
        'rgba(255, 206, 86, 0.7)',
        'rgba(199, 199, 199, 0.7)',
        'rgba(83, 102, 255, 0.7)',
        'rgba(40, 159, 64, 0.7)',
        'rgba(255, 99, 20, 0.7)'
    ];
    
    // Destroy existing chart if it exists
    if (window.topHSNChart) {
        window.topHSNChart.destroy();
    }
    
    // Create a new chart
    window.topHSNChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Frequency',
                    data: counts,
                    backgroundColor: backgroundColors,
                    borderColor: backgroundColors.map(color => color.replace('0.7', '1')),
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Count'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Most Frequent HSN Codes'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const index = context.dataIndex;
                            return [
                                `Count: ${counts[index]}`, 
                                `Total Value: ₹${parseFloat(amounts[index]).toFixed(2)}`
                            ];
                        }
                    }
                }
            }
        }
    });
}

async function loadGSTSlabDistribution() {
    try {
        // Get GST slab distribution from API
        const response = await fetch('/api/slab-distribution');
        
        if (!response.ok) {
            throw new Error(`Failed to load slab data: ${response.statusText}`);
        }
        
        const slabData = await response.json();
        
        // Create the chart
        createSlabDistributionChart(slabData);
        
    } catch (error) {
        console.error("Error loading GST slab distribution:", error);
    }
}

function createSlabDistributionChart(slabData) {
    // Get the canvas element
    const ctx = document.getElementById('slab-distribution-chart').getContext('2d');
    
    // Prepare data for Chart.js
    const labels = slabData.map(item => `${item.slab}%`);
    const counts = slabData.map(item => item.count);
    const amounts = slabData.map(item => item.total_amount);
    const taxValues = slabData.map(item => item.total_tax);
    
    // Color mapping for GST slabs
    const backgroundColors = {
        '0': 'rgba(54, 162, 235, 0.7)',
        '5': 'rgba(75, 192, 192, 0.7)',
        '12': 'rgba(153, 102, 255, 0.7)',
        '18': 'rgba(255, 159, 64, 0.7)',
        '28': 'rgba(255, 99, 132, 0.7)',
        'exempt': 'rgba(201, 203, 207, 0.7)',
        'other': 'rgba(255, 206, 86, 0.7)'
    };
    
    // Prepare colors based on labels
    const colors = labels.map(label => {
        const slab = label.replace('%', '');
        return backgroundColors[slab] || 'rgba(201, 203, 207, 0.7)';
    });
    
    // Destroy existing chart if it exists
    if (window.slabDistributionChart) {
        window.slabDistributionChart.destroy();
    }
    
    // Create a new chart
    window.slabDistributionChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [
                {
                    data: amounts,
                    backgroundColor: colors,
                    borderColor: colors.map(color => color.replace('0.7', '1')),
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'GST Slab Distribution by Value'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const index = context.dataIndex;
                            const value = parseFloat(amounts[index]).toFixed(2);
                            const percent = ((amounts[index] / amounts.reduce((sum, val) => sum + val, 0)) * 100).toFixed(1);
                            
                            return [
                                `Value: ₹${value} (${percent}%)`,
                                `Tax: ₹${parseFloat(taxValues[index]).toFixed(2)}`,
                                `Items: ${counts[index]}`
                            ];
                        }
                    }
                },
                legend: {
                    position: 'right'
                }
            }
        }
    });
}

// Setup event listeners for trend analysis
$(document).ready(function() {
    // Add event listener for the trend filter form
    $('#trend-filter-form').on('submit', function(e) {
        e.preventDefault();
        loadTrendAnalysis();
    });
    
    // Add trend-nav tab to the navbar if it doesn't exist yet
    if (!document.getElementById('trends-nav')) {
        const navbar = document.querySelector('.navbar-nav');
        if (navbar) {
            const trendsTab = document.createElement('li');
            trendsTab.className = 'nav-item';
            trendsTab.innerHTML = '<a class="nav-link" href="#" id="trends-nav"><i class="fas fa-chart-line"></i> Trends</a>';
            navbar.appendChild(trendsTab);
        }
    }
});
