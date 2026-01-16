// PesaPal RDBMS Web App JavaScript

// Track merchant being deleted
let merchantToDelete = null;

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
        } else if (tabName === 'query') {
            loadSchema();
        }
    });
});

// Schema toggle in SQL Query tab
document.addEventListener('DOMContentLoaded', () => {
    const schemaHeader = document.querySelector('.schema-section h3');
    if (schemaHeader) {
        schemaHeader.addEventListener('click', () => {
            const schemaList = document.getElementById('schema-list');
            const arrow = schemaHeader.querySelector('.toggle-arrow');
            schemaList.style.display = schemaList.style.display === 'none' ? 'block' : 'none';
            arrow.textContent = schemaList.style.display === 'none' ? '▶' : '▼';
        });
    }
});

// Load merchants
function loadMerchants() {
    fetch('/api/merchants')
        .then(response => {
            if (!response.ok) throw new Error('Failed to load merchants');
            return response.json();
        })
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
        .then(response => {
            if (!response.ok) throw new Error('Failed to load categories');
            return response.json();
        })
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

// Load and display database schema
function loadSchema() {
    fetch('/api/tables')
        .then(response => {
            if (!response.ok) throw new Error('Failed to load schema');
            return response.json();
        })
        .then(tables => {
            const container = document.getElementById('schema-list');
            
            if (tables.length === 0) {
                container.innerHTML = '<div class="empty-state"><p>No tables found in the database.</p></div>';
                return;
            }
            
            container.innerHTML = tables.map(table => `
                <div class="schema-table">
                    <div class="table-header">
                        <h3>${table.name}</h3>
                        <span class="row-count">${table.row_count} row(s)</span>
                    </div>
                    <table class="schema-columns-table">
                        <thead>
                            <tr>
                                <th>Column</th>
                                <th>Type</th>
                                <th>Primary Key</th>
                                <th>Unique</th>
                                <th>Nullable</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${table.columns.map(col => `
                                <tr>
                                    <td><code>${col.name}</code></td>
                                    <td><code>${col.data_type}</code></td>
                                    <td>${col.primary_key ? '✓' : ''}</td>
                                    <td>${col.unique ? '✓' : ''}</td>
                                    <td>${col.nullable ? '✓' : ''}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `).join('');
        })
        .catch(error => console.error('Error loading schema:', error));
}

// Open add merchant modal
function openAddMerchantModal() {
    // Load categories for the select
    fetch('/api/categories')
        .then(response => {
            if (!response.ok) throw new Error('Failed to load categories');
            return response.json();
        })
        .then(categories => {
            const select = document.getElementById('add-merchant-category');
            select.innerHTML = '<option value="">Select a category...</option>' +
                categories.map(cat => `<option value="${cat.name}">${cat.name}</option>`).join('');
        })
        .catch(error => console.error('Error loading categories:', error));
    
    // Clear form
    document.getElementById('add-merchant-form').reset();
    document.getElementById('add-merchant-message').textContent = '';
    
    // Show modal
    document.getElementById('addMerchantModal').style.display = 'block';
}

// Close add merchant modal
function closeAddMerchantModal() {
    document.getElementById('addMerchantModal').style.display = 'none';
}

// Add merchant form submission
document.addEventListener('DOMContentLoaded', () => {
    const addForm = document.getElementById('add-merchant-form');
    if (addForm) {
        addForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const id = document.getElementById('add-merchant-id').value;
            const name = document.getElementById('add-merchant-name').value;
            const category = document.getElementById('add-merchant-category').value;
            const active = document.getElementById('add-merchant-active').checked;
            
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
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                const messageDiv = document.getElementById('add-merchant-message');
                if (data.success) {
                    messageDiv.textContent = data.message;
                    messageDiv.className = 'message success';
                    setTimeout(() => {
                        closeAddMerchantModal();
                        loadMerchants();
                        showRefreshNotification('Merchant added successfully');
                    }, 500);
                } else {
                    messageDiv.textContent = data.message || 'An error occurred';
                    messageDiv.className = 'message error';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                const messageDiv = document.getElementById('add-merchant-message');
                messageDiv.textContent = 'An error occurred while adding the merchant';
                messageDiv.className = 'message error';
            });
        });
    }
});

// Delete merchant with modal
function deleteMerchant(id) {
    // Fetch merchant details for confirmation
    fetch(`/api/merchants/${id}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(merchant => {
            merchantToDelete = id;
            document.getElementById('delete-merchant-name').textContent = merchant.name;
            document.getElementById('deleteMerchantModal').style.display = 'block';
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Could not load merchant details');
        });
}

// Close delete modal
function closeDeleteModal() {
    document.getElementById('deleteMerchantModal').style.display = 'none';
    merchantToDelete = null;
}

// Confirm delete
function confirmDelete() {
    if (merchantToDelete === null) return;
    
    fetch(`/api/merchants/${merchantToDelete}`, {
        method: 'DELETE',
    })
    .then(response => {
        if (!response.ok) throw new Error('Failed to delete merchant');
        return response.json();
    })
    .then(data => {
        closeDeleteModal();
        if (data.success) {
            loadMerchants();
            showRefreshNotification('Merchant deleted successfully');
        } else {
            alert('Error: ' + (data.message || data.error));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while deleting the merchant');
        closeDeleteModal();
    });
}

// Edit merchant with modal
function editMerchant(id) {
    // Fetch merchant details
    fetch(`/api/merchants/${id}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(merchant => {
            // Load categories
            fetch('/api/categories')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to load categories');
                    }
                    return response.json();
                })
                .then(categories => {
                    // Populate form
                    document.getElementById('edit-merchant-id').value = merchant.id;
                    document.getElementById('edit-merchant-name').value = merchant.name;
                    document.getElementById('edit-merchant-active').checked = merchant.active;
                    
                    // Populate category select
                    const select = document.getElementById('edit-merchant-category');
                    select.innerHTML = '<option value="">Select a category...</option>' +
                        categories.map(cat => `<option value="${cat.name}" ${cat.name === merchant.category ? 'selected' : ''}>${cat.name}</option>`).join('');
                    
                    // Clear message
                    document.getElementById('edit-merchant-message').textContent = '';
                    
                    // Show modal
                    document.getElementById('editMerchantModal').style.display = 'block';
                })
                .catch(error => {
                    console.error('Error loading categories:', error);
                    alert('Could not load categories');
                });
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Could not load merchant details');
        });
}

// Close edit modal
function closeEditModal() {
    document.getElementById('editMerchantModal').style.display = 'none';
}

// Handle edit form submission
document.addEventListener('DOMContentLoaded', () => {
    const editForm = document.getElementById('edit-merchant-form');
    if (editForm) {
        editForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const merchantId = parseInt(document.getElementById('edit-merchant-id').value);
            const updates = {
                name: document.getElementById('edit-merchant-name').value,
                category: document.getElementById('edit-merchant-category').value,
                active: document.getElementById('edit-merchant-active').checked
            };
            
            fetch(`/api/merchants/${merchantId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(updates)
            })
            .then(response => {
                if (!response.ok) throw new Error('Failed to update merchant');
                return response.json();
            })
            .then(data => {
                const messageDiv = document.getElementById('edit-merchant-message');
                if (data.success) {
                    messageDiv.textContent = 'Merchant updated successfully';
                    messageDiv.className = 'message success';
                    setTimeout(() => {
                        closeEditModal();
                        loadMerchants();
                        showRefreshNotification('Merchant updated');
                    }, 1000);
                } else {
                    messageDiv.textContent = data.message || 'An error occurred';
                    messageDiv.className = 'message error';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                const messageDiv = document.getElementById('edit-merchant-message');
                messageDiv.textContent = 'An error occurred while updating the merchant';
                messageDiv.className = 'message error';
            });
        });
    }
});

// Close modals when clicking outside
window.addEventListener('click', (event) => {
    const addModal = document.getElementById('addMerchantModal');
    const editModal = document.getElementById('editMerchantModal');
    const deleteModal = document.getElementById('deleteMerchantModal');
    
    if (event.target === addModal) {
        closeAddMerchantModal();
    }
    if (event.target === editModal) {
        closeEditModal();
    }
    if (event.target === deleteModal) {
        closeDeleteModal();
    }
});

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
    .then(response => {
        if (!response.ok) throw new Error('Query execution failed');
        return response.json();
    })
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
loadSchema();
loadMerchants();
loadCategories();
