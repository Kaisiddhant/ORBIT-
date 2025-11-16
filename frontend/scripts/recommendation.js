// ========== AI Recommendation Functions ==========

async function getRecommendations(event) {
    event.preventDefault();
    
    const formData = {
        age: parseInt(document.getElementById('recAge').value),
        salary: parseFloat(document.getElementById('recSalary').value),
        budget: parseFloat(document.getElementById('recBudget').value) * 12, // Convert monthly to annual
        insurance_type: document.getElementById('recType').value || null
    };
    
    try {
        const data = await apiRequest('/recommendations', {
            method: 'POST',
            body: JSON.stringify(formData)
        });
        
        displayRecommendations(data.recommendations, data.user_profile);
        
    } catch (error) {
        showToast(error.message, 'error');
    }
}

function displayRecommendations(recommendations, userProfile) {
    const resultsContainer = document.getElementById('recommendationResults');
    const listContainer = document.getElementById('recommendationsList');
    
    if (recommendations.length === 0) {
        listContainer.innerHTML = '<p class="empty-state">No recommendations found matching your criteria. Try adjusting your filters.</p>';
        resultsContainer.style.display = 'block';
        return;
    }
    
    listContainer.innerHTML = recommendations.map((rec, index) => `
        <div class="recommendation-card" style="animation: slideInUp 0.3s ease ${index * 0.1}s both;">
            <div class="match-score">
                <div class="score">${rec.match_score}</div>
                <div class="label">Match</div>
            </div>
            
            <div class="recommendation-info">
                <h3>${rec.plan.name}</h3>
                <p class="provider">${rec.plan.provider} • ${rec.plan.type} Insurance</p>
                <p style="margin: 0.5rem 0; color: var(--text-light);">
                    ${rec.plan.description}
                </p>
                <div class="recommendation-features">
                    ${rec.plan.features.slice(0, 5).map(feature => `
                        <span class="feature-tag">${feature}</span>
                    `).join('')}
                </div>
            </div>
            
            <div class="recommendation-pricing">
                <div class="annual-premium">${formatCurrency(rec.estimated_premium)}</div>
                <div class="monthly-premium">${formatCurrency(rec.monthly_premium)}/month</div>
                <span class="affordability ${rec.affordability.toLowerCase()}">${rec.affordability} Affordability</span>
                <div style="margin-top: 1rem; display: flex; flex-direction: column; gap: 0.5rem;">
                    <button class="btn btn-primary" onclick="purchasePlan(${rec.plan.id})">
                        <i class="fas fa-check"></i> Select Plan
                    </button>
                    <button class="btn btn-outline" onclick="saveQuote(${rec.plan.id})">
                        <i class="fas fa-bookmark"></i> Save Quote
                    </button>
                </div>
            </div>
        </div>
    `).join('');
    
    // Add animation styles
    if (!document.getElementById('rec-animations')) {
        const style = document.createElement('style');
        style.id = 'rec-animations';
        style.textContent = `
            @keyframes slideInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    resultsContainer.style.display = 'block';
    
    // Scroll to results
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    showToast(`Found ${recommendations.length} personalized recommendations!`, 'success');
}

// ========== Premium Estimation ==========
async function estimatePremium(planId, age, salary) {
    try {
        const data = await apiRequest('/premium-estimate', {
            method: 'POST',
            body: JSON.stringify({
                plan_id: planId,
                age: age,
                salary: salary
            })
        });
        
        return data;
        
    } catch (error) {
        console.error('Error estimating premium:', error);
        return null;
    }
}