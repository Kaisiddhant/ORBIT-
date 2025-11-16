// ========== Dashboard Functions ==========

let currentSection = 'overview';

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname.includes('dashboard.html')) {
        if (!requireAuth()) return;
        
        initDashboard();
        setupSidebarNavigation();
        loadDashboardData();
    }
});

function initDashboard() {
    const user = getCurrentUser();
    if (user) {
        document.getElementById('userName').textContent = user.full_name || user.email;
        
        // Set profile form values
        if (document.getElementById('profileName')) {
            document.getElementById('profileName').value = user.full_name || '';
            document.getElementById('profileEmail').value = user.email || '';
            document.getElementById('profileAge').value = user.age || '';
            document.getElementById('profileSalary').value = user.salary || '';
            document.getElementById('profilePhone').value = user.phone || '';
        }
        
        // Set recommendation form defaults
        if (document.getElementById('recAge')) {
            document.getElementById('recAge').value = user.age || '';
            document.getElementById('recSalary').value = user.salary || '';
            
            // Set default budget (5% of salary)
            if (user.salary) {
                document.getElementById('recBudget').value = Math.round(user.salary * 0.05 / 12);
            }
        }
    }
}

async function loadDashboardData() {
    try {
        // Load stats
        const stats = await apiRequest('/dashboard/stats');
        updateDashboardStats(stats);
        
        // Load recent policies
        const policiesData = await apiRequest('/policies');
        displayRecentPolicies(policiesData.policies.slice(0, 3));
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

function updateDashboardStats(stats) {
    document.getElementById('activePolicies').textContent = stats.active_policies;
    document.getElementById('totalCoverage').textContent = formatCurrency(stats.total_coverage);
    document.getElementById('totalPremium').textContent = formatCurrency(stats.total_annual_premium);
    document.getElementById('savedQuotes').textContent = stats.saved_quotes;
}

function displayRecentPolicies(policies) {
    const container = document.getElementById('recentPolicies');
    
    if (policies.length === 0) {
        container.innerHTML = '<p class="empty-state">No policies yet. Get recommendations to find your perfect plan!</p>';
        return;
    }
    
    container.innerHTML = policies.map(policy => `
        <div class="policy-item">
            <div class="policy-info">
                <h4>${policy.plan.name}</h4>
                <p>${policy.plan.type} Insurance • ${policy.policy_number}</p>
            </div>
            <span class="policy-badge">${policy.status}</span>
        </div>
    `).join('');
}

// ========== Sidebar Navigation ==========
function setupSidebarNavigation() {
    const navItems = document.querySelectorAll('.sidebar-nav .nav-item');
    
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const section = item.dataset.section;
            switchSection(section);
        });
    });
}

function switchSection(sectionName) {
    // Update active nav item
    document.querySelectorAll('.sidebar-nav .nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.section === sectionName) {
            item.classList.add('active');
        }
    });
    
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Show selected section
    document.getElementById(sectionName).classList.add('active');
    
    // Update page title
    const titles = {
        overview: 'Dashboard Overview',
        recommendations: 'AI Recommendations',
        compare: 'Compare Plans',
        policies: 'My Policies',
        quotes: 'Saved Quotes',
        profile: 'Profile Settings'
    };
    document.getElementById('pageTitle').textContent = titles[sectionName];
    
    // Load section-specific data
    loadSectionData(sectionName);
    
    // Close sidebar on mobile
    if (window.innerWidth <= 768) {
        toggleSidebar();
    }
}

async function loadSectionData(section) {
    switch (section) {
        case 'policies':
            await loadPolicies();
            break;
        case 'quotes':
            await loadQuotes();
            break;
        case 'compare':
            await loadPlansForComparison();
            break;
    }
}

// ========== Sidebar Toggle ==========
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('active');
}

// ========== Profile Update ==========
async function updateProfile(event) {
    event.preventDefault();
    
    const formData = {
        full_name: document.getElementById('profileName').value,
        age: parseInt(document.getElementById('profileAge').value) || null,
        salary: parseFloat(document.getElementById('profileSalary').value) || null,
        phone: document.getElementById('profilePhone').value || null
    };
    
    try {
        const data = await apiRequest('/user/profile', {
            method: 'PUT',
            body: JSON.stringify(formData)
        });
        
        // Update local storage
        localStorage.setItem('user', JSON.stringify(data.user));
        
        // Update UI
        document.getElementById('userName').textContent = data.user.full_name || data.user.email;
        
        showToast('Profile updated successfully!', 'success');
        
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// ========== Policies Management ==========
async function loadPolicies() {
    try {
        const data = await apiRequest('/policies');
        displayPolicies(data.policies);
    } catch (error) {
        console.error('Error loading policies:', error);
    }
}

function displayPolicies(policies) {
    const container = document.getElementById('policiesList');
    
    if (policies.length === 0) {
        container.innerHTML = '<p class="empty-state">No policies found. Get AI recommendations to find your perfect plan!</p>';
        return;
    }
    
    container.innerHTML = policies.map(policy => `
        <div class="policy-card">
            <div class="policy-card-header">
                <div>
                    <div class="policy-number">Policy #${policy.policy_number}</div>
                    <h3>${policy.plan.name}</h3>
                </div>
                <span class="policy-status ${policy.status}">${policy.status}</span>
            </div>
            <div class="policy-details">
                <p><strong>Provider:</strong> ${policy.plan.provider}</p>
                <p><strong>Type:</strong> ${policy.plan.type} Insurance</p>
                <p><strong>Coverage:</strong> ${formatCurrency(policy.coverage_amount)}</p>
                <p><strong>Start Date:</strong> ${formatDate(policy.start_date)}</p>
            </div>
            <div class="policy-price">${formatCurrency(policy.premium)}<small>/year</small></div>
            <div class="policy-actions">
                <button class="btn btn-primary" onclick="downloadPolicy(${policy.id})">
                    <i class="fas fa-download"></i> Download PDF
                </button>
                <button class="btn btn-outline" onclick="viewPolicyDetails(${policy.id})">
                    <i class="fas fa-eye"></i> View Details
                </button>
            </div>
        </div>
    `).join('');
}

async function downloadPolicy(policyId) {
    try {
        const token = getAuthToken();
        const response = await fetch(`${API_BASE_URL}/policies/${policyId}/download`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) throw new Error('Download failed');
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `policy_${policyId}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showToast('Policy downloaded successfully!', 'success');
        
    } catch (error) {
        showToast('Failed to download policy', 'error');
    }
}

function viewPolicyDetails(policyId) {
    // This would open a modal with detailed policy information
    showToast('Policy details coming soon', 'error');
}

// ========== Quotes Management ==========
async function loadQuotes() {
    try {
        const data = await apiRequest('/quotes');
        displayQuotes(data.quotes);
    } catch (error) {
        console.error('Error loading quotes:', error);
    }
}

function displayQuotes(quotes) {
    const container = document.getElementById('quotesList');
    
    if (quotes.length === 0) {
        container.innerHTML = '<p class="empty-state">No saved quotes yet.</p>';
        return;
    }
    
    container.innerHTML = quotes.map(quote => `
        <div class="quote-card">
            <div class="plan-header">
                <span class="plan-type">${quote.plan.type}</span>
                <h3 class="plan-name">${quote.plan.name}</h3>
                <p class="plan-provider">${quote.plan.provider}</p>
            </div>
            <div class="plan-price">
                ${formatCurrency(quote.estimated_premium)}
                <small>/year</small>
            </div>
            <p style="color: var(--text-light); font-size: 0.9rem; margin: 1rem 0;">
                Saved on ${formatDate(quote.created_at)}
            </p>
            <div class="plan-actions">
                <button class="btn btn-primary" onclick="purchasePlan(${quote.plan.id})">
                    Purchase Now
                </button>
                <button class="btn btn-outline" onclick="viewPlanDetails(${quote.plan.id})">
                    View Details
                </button>
            </div>
        </div>
    `).join('');
}

// ========== Comparison ==========
let selectedPlansForComparison = [];

async function loadPlansForComparison() {
    try {
        const data = await apiRequest('/plans');
        displayPlansForComparison(data.plans);
    } catch (error) {
        console.error('Error loading plans:', error);
    }
}

function displayPlansForComparison(plans) {
    const container = document.getElementById('comparePlansGrid');
    
    container.innerHTML = plans.map(plan => `
        <div class="plan-card">
            <div class="select-compare">
                <input type="checkbox" 
                       id="compare-${plan.id}" 
                       value="${plan.id}"
                       onchange="togglePlanSelection(${plan.id}, this.checked)"
                       ${selectedPlansForComparison.includes(plan.id) ? 'checked' : ''}>
            </div>
            <div class="plan-header">
                <span class="plan-type">${plan.type}</span>
                <h3 class="plan-name">${plan.name}</h3>
                <p class="plan-provider">${plan.provider}</p>
            </div>
            <div class="plan-price">
                ${formatCurrency(plan.base_premium)}
                <small>/year</small>
            </div>
        </div>
    `).join('');
}

function togglePlanSelection(planId, isSelected) {
    if (isSelected) {
        if (selectedPlansForComparison.length >= 4) {
            showToast('You can compare maximum 4 plans', 'error');
            document.getElementById(`compare-${planId}`).checked = false;
            return;
        }
        selectedPlansForComparison.push(planId);
    } else {
        selectedPlansForComparison = selectedPlansForComparison.filter(id => id !== planId);
    }
    
    updateCompareSelection();
}

function updateCompareSelection() {
    const container = document.getElementById('compareSelection');
    const compareBtn = document.getElementById('compareBtn');
    
    container.innerHTML = selectedPlansForComparison.map(id => {
        const plan = allPlans.find(p => p.id === id);
        return `
            <div class="compare-chip">
                <span>${plan ? plan.name : `Plan ${id}`}</span>
                <span class="remove" onclick="togglePlanSelection(${id}, false); document.getElementById('compare-${id}').checked = false;">×</span>
            </div>
        `;
    }).join('');
    
    compareBtn.disabled = selectedPlansForComparison.length < 2;
}

async function compareSelectedPlans() {
    if (selectedPlansForComparison.length < 2) {
        showToast('Please select at least 2 plans to compare', 'error');
        return;
    }
    
    try {
        const data = await apiRequest('/compare', {
            method: 'POST',
            body: JSON.stringify({ plan_ids: selectedPlansForComparison })
        });
        
        displayComparison(data.comparison);
        
    } catch (error) {
        showToast(error.message, 'error');
    }
}

function displayComparison(comparison) {
    const container = document.getElementById('comparisonTable');
    
    container.innerHTML = `
        <h3>Plan Comparison</h3>
        <table class="comparison-table">
            <thead>
                <tr>
                    <th>Feature</th>
                    ${comparison.map(item => `<th>${item.plan.name}</th>`).join('')}
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>Provider</strong></td>
                    ${comparison.map(item => `<td>${item.plan.provider}</td>`).join('')}
                </tr>
                <tr>
                    <td><strong>Type</strong></td>
                    ${comparison.map(item => `<td>${item.plan.type}</td>`).join('')}
                </tr>
                <tr>
                    <td><strong>Coverage Amount</strong></td>
                    ${comparison.map(item => `<td>${formatCurrency(item.plan.coverage_amount)}</td>`).join('')}
                </tr>
                <tr>
                    <td><strong>Annual Premium</strong></td>
                    ${comparison.map(item => `<td><strong>${formatCurrency(item.estimated_premium)}</strong></td>`).join('')}
                </tr>
                <tr>
                    <td><strong>Monthly Premium</strong></td>
                    ${comparison.map(item => `<td>${formatCurrency(item.monthly_premium)}</td>`).join('')}
                </tr>
                <tr>
                    <td><strong>Coverage per Dollar</strong></td>
                    ${comparison.map(item => `<td>${formatCurrency(item.coverage_per_dollar)}</td>`).join('')}
                </tr>
                <tr>
                    <td><strong>Rating</strong></td>
                    ${comparison.map(item => `<td>${item.plan.rating} ⭐</td>`).join('')}
                </tr>
                <tr>
                    <td><strong>Action</strong></td>
                    ${comparison.map(item => `
                        <td>
                            <button class="btn btn-primary" onclick="purchasePlan(${item.plan.id})">
                                Select
                            </button>
                        </td>
                    `).join('')}
                </tr>
            </tbody>
        </table>
    `;
    
    container.style.display = 'block';
}

function addToComparison(planId) {
    // Navigate to compare section and select the plan
    switchSection('compare');
    setTimeout(() => {
        const checkbox = document.getElementById(`compare-${planId}`);
        if (checkbox) {
            checkbox.checked = true;
            togglePlanSelection(planId, true);
        }
    }, 500);
}