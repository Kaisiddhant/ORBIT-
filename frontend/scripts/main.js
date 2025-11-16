// ========== Configuration ==========
const API_BASE_URL = 'http://localhost:5000/api';

// ========== Utility Functions ==========
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0
    }).format(amount);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function showError(elementId, message) {
    const errorElement = document.getElementById(elementId);
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.classList.add('show');
        setTimeout(() => {
            errorElement.classList.remove('show');
        }, 5000);
    }
}

function showToast(message, type = 'success') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Add styles
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#4caf50' : '#f44336'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        gap: 10px;
        z-index: 10000;
        animation: slideInRight 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Add animations to head
if (!document.getElementById('toast-animations')) {
    const style = document.createElement('style');
    style.id = 'toast-animations';
    style.textContent = `
        @keyframes slideInRight {
            from { transform: translateX(400px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOutRight {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(400px); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
}

// ========== Navigation Functions ==========
function toggleMobileMenu() {
    const navMenu = document.getElementById('navMenu');
    navMenu.classList.toggle('active');
}

function scrollToPlans() {
    document.getElementById('plans').scrollIntoView({ behavior: 'smooth' });
}

// Smooth scroll for navigation links
document.addEventListener('DOMContentLoaded', () => {
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const href = link.getAttribute('href');
            if (href.startsWith('#')) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                    // Close mobile menu if open
                    const navMenu = document.getElementById('navMenu');
                    if (navMenu) {
                        navMenu.classList.remove('active');
                    }
                }
            }
        });
    });
});

// Highlight active nav link on scroll
window.addEventListener('scroll', () => {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link');
    
    let current = '';
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (pageYOffset >= sectionTop - 200) {
            current = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active');
        }
    });
});

// ========== Modal Functions ==========
function openLoginModal() {
    const modal = document.getElementById('loginModal');
    modal.classList.add('show');
    modal.style.display = 'flex';
}

function closeLoginModal() {
    const modal = document.getElementById('loginModal');
    modal.classList.remove('show');
    setTimeout(() => {
        modal.style.display = 'none';
    }, 300);
}

function openSignupModal() {
    const modal = document.getElementById('signupModal');
    modal.classList.add('show');
    modal.style.display = 'flex';
}

function closeSignupModal() {
    const modal = document.getElementById('signupModal');
    modal.classList.remove('show');
    setTimeout(() => {
        modal.style.display = 'none';
    }, 300);
}

function openPlanModal(planId) {
    fetchPlanDetails(planId);
}

function closePlanModal() {
    const modal = document.getElementById('planModal');
    modal.classList.remove('show');
    setTimeout(() => {
        modal.style.display = 'none';
    }, 300);
}

// Close modal when clicking outside
window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('show');
        setTimeout(() => {
            e.target.style.display = 'none';
        }, 300);
    }
});

// ========== API Functions ==========
async function apiRequest(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
        }
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'An error occurred');
    }

    return response.json();
}

// ========== Plans Functions ==========
let allPlans = [];
let currentFilter = 'all';

async function loadPlans() {
    try {
        const data = await apiRequest('/plans');
        allPlans = data.plans;
        displayPlans(allPlans);
        setupPlanFilters();
    } catch (error) {
        console.error('Error loading plans:', error);
        document.getElementById('plansGrid').innerHTML = `
            <div class="error-message show">
                Failed to load insurance plans. Please try again later.
            </div>
        `;
    }
}

function displayPlans(plans) {
    const grid = document.getElementById('plansGrid');
    
    if (plans.length === 0) {
        grid.innerHTML = '<p class="empty-state">No plans found matching your criteria.</p>';
        return;
    }

    grid.innerHTML = plans.map(plan => `
        <div class="plan-card" data-type="${plan.type}">
            <div class="plan-header">
                <span class="plan-type">${plan.type}</span>
                <h3 class="plan-name">${plan.name}</h3>
                <p class="plan-provider">${plan.provider}</p>
            </div>
            <div class="plan-price">
                ${formatCurrency(plan.base_premium)}
                <small>/year</small>
            </div>
            <p class="plan-description">${plan.description}</p>
            <ul class="plan-features">
                ${plan.features.slice(0, 4).map(feature => `
                    <li><i class="fas fa-check-circle"></i> ${feature}</li>
                `).join('')}
            </ul>
            <div class="plan-actions">
                <button class="btn btn-primary" onclick="viewPlanDetails(${plan.id})">
                    View Details
                </button>
                ${localStorage.getItem('token') ? `
                    <button class="btn btn-outline" onclick="addToComparison(${plan.id})">
                        <i class="fas fa-balance-scale"></i>
                    </button>
                ` : ''}
            </div>
        </div>
    `).join('');
}

function setupPlanFilters() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    
    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active state
            filterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Filter plans
            const type = btn.dataset.type;
            currentFilter = type;
            
            const filteredPlans = type === 'all' 
                ? allPlans 
                : allPlans.filter(plan => plan.type === type);
            
            displayPlans(filteredPlans);
        });
    });
}

async function viewPlanDetails(planId) {
    try {
        const data = await apiRequest(`/plans/${planId}`);
        const plan = data.plan;
        
        const modal = document.getElementById('planModal');
        const content = document.getElementById('planModalContent');
        
        content.innerHTML = `
            <div class="plan-detail-header">
                <span class="plan-type">${plan.type} Insurance</span>
                <h2>${plan.name}</h2>
                <p class="plan-provider">${plan.provider}</p>
            </div>
            
            <div class="plan-detail-body">
                <div class="plan-detail-section">
                    <h3>Coverage Details</h3>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <label>Coverage Amount</label>
                            <strong>${formatCurrency(plan.coverage_amount)}</strong>
                        </div>
                        <div class="detail-item">
                            <label>Base Premium</label>
                            <strong>${formatCurrency(plan.base_premium)}/year</strong>
                        </div>
                        <div class="detail-item">
                            <label>Age Eligibility</label>
                            <strong>${plan.age_range[0]} - ${plan.age_range[1]} years</strong>
                        </div>
                        <div class="detail-item">
                            <label>Rating</label>
                            <strong>${plan.rating} <i class="fas fa-star" style="color: #ffa500;"></i></strong>
                        </div>
                    </div>
                </div>
                
                <div class="plan-detail-section">
                    <h3>Features & Benefits</h3>
                    <ul class="features-list">
                        ${plan.features.map(feature => `
                            <li><i class="fas fa-check-circle"></i> ${feature}</li>
                        `).join('')}
                    </ul>
                </div>
                
                <div class="plan-detail-section">
                    <h3>Description</h3>
                    <p>${plan.description}</p>
                </div>
                
                ${localStorage.getItem('token') ? `
                    <div class="plan-detail-actions">
                        <button class="btn btn-primary btn-large" onclick="purchasePlan(${plan.id})">
                            <i class="fas fa-shopping-cart"></i> Purchase Plan
                        </button>
                        <button class="btn btn-outline btn-large" onclick="saveQuote(${plan.id})">
                            <i class="fas fa-bookmark"></i> Save for Later
                        </button>
                    </div>
                ` : `
                    <div class="plan-detail-actions">
                        <p style="text-align: center; color: var(--text-light);">
                            Please <a href="#" onclick="closePlanModal(); openLoginModal();">login</a> to purchase this plan
                        </p>
                    </div>
                `}
            </div>
        `;
        
        modal.classList.add('show');
        modal.style.display = 'flex';
        
    } catch (error) {
        console.error('Error loading plan details:', error);
        showToast('Failed to load plan details', 'error');
    }
}

async function purchasePlan(planId) {
    try {
        const data = await apiRequest('/policies', {
            method: 'POST',
            body: JSON.stringify({ plan_id: planId })
        });
        
        showToast('Policy created successfully!', 'success');
        closePlanModal();
        
        // Redirect to dashboard after 1 second
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 1000);
        
    } catch (error) {
        console.error('Error purchasing plan:', error);
        showToast(error.message, 'error');
    }
}

async function saveQuote(planId) {
    try {
        await apiRequest('/quotes', {
            method: 'POST',
            body: JSON.stringify({ plan_id: planId })
        });
        
        showToast('Quote saved successfully!', 'success');
        closePlanModal();
        
    } catch (error) {
        console.error('Error saving quote:', error);
        showToast(error.message, 'error');
    }
}

// ========== Initialize ==========
document.addEventListener('DOMContentLoaded', () => {
    // Load plans if on home page
    if (document.getElementById('plansGrid')) {
        loadPlans();
    }
    
    // Check authentication status
    const token = localStorage.getItem('token');
    if (token && window.location.pathname.includes('dashboard.html')) {
        // User is logged in and on dashboard - good
    } else if (token && window.location.pathname.includes('index.html')) {
        // User is logged in but on home page - update nav
        updateNavForLoggedInUser();
    } else if (!token && window.location.pathname.includes('dashboard.html')) {
        // User not logged in but trying to access dashboard
        window.location.href = 'index.html';
    }
});

function updateNavForLoggedInUser() {
    const navActions = document.querySelector('.nav-actions');
    if (navActions) {
        navActions.innerHTML = `
            <button class="btn btn-primary" onclick="window.location.href='dashboard.html'">
                Dashboard
            </button>
            <button class="btn btn-outline" onclick="handleLogout()">
                Logout
            </button>
        `;
    }
}

// ========== Google Sign-In ==========
function initGoogleSignIn() {
    // This is a placeholder for Google Sign-In initialization
    // You would need to add the Google Sign-In SDK and configure it
    console.log('Google Sign-In initialized');
}