// PesaPal RDBMS Web App JavaScript

// Tab switching
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        const tabName = button.dataset.tab;
        
        // Remove active class from all buttons and content
        document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        // Add active class to clicked button and corresponding content
        button.classList.add('active');
        document.getElementById(tabName).classList.add('active');
        
        // Load content when tab is opened
        if (tabName === 'merchants') {
            loadMerchants();
        } else if (tabName === 'categories') {
            loadCategories();
        }
    });
});

// Load merchants
function loadMerchants() {
    fetch('/api/merchants')
        .then(response => response.json())
        .then(merchants => {
            const container = document.getElementById('merchants-list');
            
            if (merchants.length === 0) {
                container.innerHTML = '<div class="empty-state"><p>No merchants found. Add one to get started!</p></div>';
                return;
            }
            
            container.innerHTML = merchants.map(merchant => `
                <div class="merchant-card">
                    <h3>${merchant.name}</h3>
                    <div class="info">
                        <span class="label">ID:</span> ${merchant.id}
                    </div>
                    <div class="info">
                        <span class="label">Category:</span> ${merchant.category}
                    </div>
                    <div class="status ${merchant.active ? 'active' : 'inactive'}">
                        ${merchant.active ? '✓ Active' : '✗ Inactive'}
                    </div>
                    <div class="actions">
                        <button class="btn-edit" onclick="editMerchant(${merchant.id})">Edit</button>
                        <button class="btn-delete" onclick="deleteMerchant(${merchant.id})">Delete</button>
                    </div>
                </div>
            `).join('');
        })
        .catch(error => console.error('Error loading merchants:', error));
}

// Load categories and populate form
function loadCategories() {
    fetch('/api/categories')
        .then(response => response.json())
        .then(categories => {
            // Update categories display
            const container = document.getElementById('categories-list');
            
            if (categories.length === 0) {
                container.innerHTML = '<div class="empty-state"><p>No categories found.</p></div>';
                return;
            }
            
            container.innerHTML = categories.map(cat => `
                <div class="category-card">
                    <h3>${cat.name}</h3>
                    <p>${cat.description || 'No description'}</p>
                </div>
            `).join('');
            
            // Update form select
            const select = document.getElementById('merchant-category');
            const currentValue = select.value;
            select.innerHTML = '<option value="">Select a category...</option>' + 
                categories.map(cat => `<option value="${cat.name}">${cat.name}</option>`).join('');
            select.value = currentValue;
        })
        .catch(error => console.error('Error loading categories:', error));
}

// Add merchant
document.getElementById('add-merchant-form').addEventListener('submit', (e) => {
    e.preventDefault();
    
    const id = document.getElementById('merchant-id').value;
    const name = document.getElementById('merchant-name').value;
    const category = document.getElementById('merchant-category').value;
    const active = document.getElementById('merchant-active').checked;
    
    fetch('/api/merchants', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            id: parseInt(id),
            name: name,
            category: category,
            active: active,
        }),
    })
    .then(response => response.json())
    .then(data => {
        const messageDiv = document.getElementById('add-merchant-message');
        if (data.success) {
            messageDiv.textContent = data.message;
            messageDiv.className = 'message success';
            document.getElementById('add-merchant-form').reset();
            
            // Reload merchants list
            setTimeout(() => loadMerchants(), 1000);
        } else {
            messageDiv.textContent = data.error || 'An error occurred';
            messageDiv.className = 'message error';
        }
        
        // Clear message after 5 seconds
        setTimeout(() => {
            messageDiv.className = 'message';
        }, 5000);
    })
    .catch(error => {
        console.error('Error:', error);
        const messageDiv = document.getElementById('add-merchant-message');
        messageDiv.textContent = 'An error occurred while adding the merchant';
        messageDiv.className = 'message error';
    });
});

// Delete merchant
function deleteMerchant(id) {
    if (confirm('Are you sure you want to delete this merchant?')) {
        fetch(`/api/merchants/${id}`, {
            method: 'DELETE',
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadMerchants();
                alert('Merchant deleted successfully');
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while deleting the merchant');
        });
    }
}

// Edit merchant (placeholder)
function editMerchant(id) {
    alert('Edit functionality would be implemented here for merchant ' + id);
    // In a full implementation, this would open an edit form
}

// Execute SQL query
function executeQuery() {
    const sql = document.getElementById('sql-query').value.trim();
    
    if (!sql) {
        alert('Please enter a SQL query');
        return;
    }
    
    fetch('/api/query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ sql: sql }),
    })
    .then(response => response.json())
    .then(data => {
        const resultDiv = document.getElementById('query-result');
        
        if (data.success) {
            let html = `<div class="success-message">${data.message}</div>`;
            
            if (data.data && data.data.length > 0) {
                const columns = Object.keys(data.data[0]);
                html += '<table>';
                html += '<thead><tr>';
                
                // Table header
                columns.forEach(col => {
                    html += `<th>${col}</th>`;
                });
                html += '</tr></thead>';
                
                // Table body
                html += '<tbody>';
                data.data.forEach(row => {
                    html += '<tr>';
                    columns.forEach(col => {
                        html += `<td>${row[col] !== null ? row[col] : 'NULL'}</td>`;
                    });
                    html += '</tr>';
                });
                html += '</tbody></table>';
            }
            
            resultDiv.innerHTML = html;
            resultDiv.classList.add('active');
            
            // Auto-refresh affected tables based on query type and affected table
            const sqlUpper = sql.toUpperCase();
            if (sqlUpper.includes('INSERT') || sqlUpper.includes('UPDATE') || sqlUpper.includes('DELETE')) {
                // Use the affected_table from the API response for accuracy
                const affectedTable = data.affected_table;
                
                if (affectedTable === 'merchants' || affectedTable === 'MERCHANTS') {
                    setTimeout(() => {
                        loadMerchants();
                        showRefreshNotification('Merchants list updated');
                    }, 300);
                }
                if (affectedTable === 'categories' || affectedTable === 'CATEGORIES') {
                    setTimeout(() => {
                        loadCategories();
                        showRefreshNotification('Categories list updated');
                    }, 300);
                }
            }
        } else {
            resultDiv.innerHTML = `<div class="error">Error: ${data.message}</div>`;
            resultDiv.classList.add('active');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        const resultDiv = document.getElementById('query-result');
        resultDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
        resultDiv.classList.add('active');
    });
}

// Show temporary notification
function showRefreshNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'refresh-notification';
    notification.textContent = '✓ ' + message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background-color: #4caf50;
        color: white;
        padding: 12px 20px;
        border-radius: 4px;
        font-size: 14px;
        z-index: 1000;
        animation: slideIn 0.3s ease-in-out;
    `;
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Load initial data
loadMerchants();
loadCategories();
