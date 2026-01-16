// PesaPal RDBMS Web App JavaScript

// Track merchant being deleted
let merchantToDelete = null;

// Query result state
let lastQueryResult = null;
let queryHistory = [];
const MAX_HISTORY = 5;

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
                        <button class="btn-edit" onclick="editMerchant(${parseInt(merchant.id)})">Edit</button>
                        <button class="btn-delete" onclick="deleteMerchant(${parseInt(merchant.id)})">Delete</button>
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
        if (data.success) {
            renderResults(data, sql);
            lastQueryResult = data;
            addToHistory(sql, data);
            
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
            const resultDiv = document.getElementById('query-result');
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

// Clear SQL Query input
function clearQuery() {
    document.getElementById('sql-query').value = '';
    document.getElementById('sql-query').focus();
}

// Toggle statement details section
function toggleStatementDetailsSection() {
    const section = document.getElementById('statement-details-section');
    const arrow = document.getElementById('statement-details-arrow');
    
    if (section.style.display === 'none') {
        section.style.display = 'block';
        arrow.textContent = '▼';
    } else {
        section.style.display = 'none';
        arrow.textContent = '▶';
    }
}

// Render results with collapsible statement details section
function renderResults(data, sql) {
    const resultDiv = document.getElementById('query-result');
    let html = `<div class="success-message">${data.message}</div>`;
    
    // Always show statement details as collapsible section
    if (Array.isArray(data.data) && data.data.length > 0 && data.data[0].statement) {
        // Show collapsible statements section
        let statementIndex = 0;
        
        html += `<div style="margin-top: 20px;">`;
        html += `<div onclick="toggleStatementDetailsSection()" style="padding: 12px; background: #f5f5f5; cursor: pointer; display: flex; align-items: center; gap: 10px; user-select: none; border-radius: 5px; margin-bottom: 10px;">`;
        html += `<span id="statement-details-arrow" style="font-size: 12px;">▶</span>`;
        html += `<h3 style="margin: 0; color: #2c3e50;">📋 Statement Details</h3>`;
        html += `</div>`;
        html += `<div id="statement-details-section" style="display: none;">`;
        
        data.data.forEach((result, idx) => {
            if (!result.is_table_contents) {
                html += `<div style="margin-bottom: 8px; padding: 12px; background: #f9f9f9; border-left: 3px solid #3498db; border-radius: 3px;">`;
                html += `<strong>Statement ${statementIndex + 1}:</strong> ${result.message}`;
                
                if (result.data && result.data.length > 0 && typeof result.data[0] === 'object') {
                    const columns = Object.keys(result.data[0]);
                    html += '<table style="margin-top: 8px; width: 100%; border-collapse: collapse; font-size: 12px;">';
                    html += '<thead><tr style="background: #e3f2fd;">';
                    columns.forEach(col => {
                        html += `<th style="padding: 6px; text-align: left; border: 1px solid #ddd;">${col}</th>`;
                    });
                    html += '</tr></thead>';
                    html += '<tbody>';
                    result.data.forEach(row => {
                        html += '<tr>';
                        columns.forEach(col => {
                            html += `<td style="padding: 6px; border: 1px solid #ddd;">${row[col] !== null ? row[col] : 'NULL'}</td>`;
                        });
                        html += '</tr>';
                    });
                    html += '</tbody></table>';
                }
                
                html += `</div>`;
                statementIndex++;
            }
        });
        
        html += `</div></div>`;
        
        // Always show final table contents
        let tableContentsStarted = false;
        
        data.data.forEach((result) => {
            if (result.is_table_contents) {
                if (!tableContentsStarted) {
                    html += `<div style="margin-top: 30px; border-top: 3px solid #2196F3; padding-top: 20px;">`;
                    html += `<h3 style="color: #2196F3; margin: 0 0 15px 0;">📊 Final Table Contents</h3>`;
                    tableContentsStarted = true;
                }
                
                html += `<div style="margin-bottom: 20px; padding: 15px; background: #f9f9f9; border-radius: 8px; border-left: 4px solid #4CAF50;">`;
                html += `<h4 style="color: #4CAF50; margin: 0 0 10px 0;">${result.table}</h4>`;
                html += `<p style="margin: 0 0 10px 0; color: #666; font-size: 13px;">${result.message}</p>`;
                
                if (result.data && result.data.length > 0) {
                    const columns = Object.keys(result.data[0]);
                    html += '<table style="width: 100%; border-collapse: collapse;">';
                    html += '<thead><tr style="background: #4CAF50; color: white;">';
                    columns.forEach(col => {
                        html += `<th style="padding: 12px; text-align: left; border: 1px solid #ddd;">${col}</th>`;
                    });
                    html += '</tr></thead>';
                    html += '<tbody>';
                    result.data.forEach((row, rowIdx) => {
                        html += `<tr style="background: ${rowIdx % 2 === 0 ? '#fff' : '#f5f5f5'};">`;
                        columns.forEach(col => {
                            html += `<td style="padding: 10px; border: 1px solid #ddd;">${row[col] !== null ? row[col] : 'NULL'}</td>`;
                        });
                        html += '</tr>';
                    });
                    html += '</tbody></table>';
                }
                html += '</div>';
            }
        });
        
        if (tableContentsStarted) {
            html += '</div>';
        }
    } else if (data.data && data.data.length > 0 && typeof data.data[0] === 'object') {
        // Single statement with table results
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
}

// Export results as JSON or CSV
function exportResults(format) {
    if (!lastQueryResult) {
        alert('No results to export');
        return;
    }
    
    const data = lastQueryResult.data;
    const timestamp = new Date().toISOString().slice(0, 10);
    
    if (format === 'json') {
        const jsonData = JSON.stringify(data, null, 2);
        downloadFile(jsonData, `query-results-${timestamp}.json`, 'application/json');
    } else if (format === 'csv') {
        // Extract table contents and convert to CSV
        let csvContent = '';
        
        if (Array.isArray(data.data) && data.data.length > 0) {
            data.data.forEach((result) => {
                if (result.is_table_contents && result.data && result.data.length > 0) {
                    csvContent += `\n"${result.table}"\n`;
                    const columns = Object.keys(result.data[0]);
                    csvContent += columns.join(',') + '\n';
                    
                    result.data.forEach(row => {
                        csvContent += columns.map(col => {
                            const val = row[col] !== null ? row[col] : '';
                            return `"${String(val).replace(/"/g, '""')}"`;
                        }).join(',') + '\n';
                    });
                }
            });
        }
        
        downloadFile(csvContent, `query-results-${timestamp}.csv`, 'text/csv');
    }
}

// Helper function to download file
function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

// Add query to history
function addToHistory(sql, result) {
    queryHistory.unshift({
        sql: sql,
        timestamp: new Date().toLocaleString(),
        message: result.message
    });
    
    // Keep only recent queries
    if (queryHistory.length > MAX_HISTORY) {
        queryHistory.pop();
    }
    
    updateHistoryDisplay();
}

// Update history display
function updateHistoryDisplay() {
    const historyDiv = document.getElementById('query-history');
    const countSpan = document.getElementById('history-count');
    
    if (queryHistory.length === 0) {
        historyDiv.innerHTML = '<p class="empty-state">No queries executed yet</p>';
        countSpan.textContent = '(0)';
        return;
    }
    
    countSpan.textContent = `(${queryHistory.length})`;
    historyDiv.innerHTML = queryHistory.map((item, idx) => `
        <div class="history-item">
            <div class="history-header">
                <span class="history-time">${item.timestamp}</span>
                <button class="btn-history" onclick="loadFromHistory(${idx})" title="Re-run query">↻</button>
            </div>
            <code class="history-sql">${item.sql}</code>
            <p class="history-message">${item.message}</p>
        </div>
    `).join('');
}

// Load query from history
function loadFromHistory(index) {
    if (index >= 0 && index < queryHistory.length) {
        document.getElementById('sql-query').value = queryHistory[index].sql;
        document.getElementById('sql-query').focus();
    }
}

