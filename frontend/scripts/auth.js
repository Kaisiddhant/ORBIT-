// ========== Authentication Functions ==========

async function handleLogin(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoader = submitBtn.querySelector('.btn-loader');
    
    // Get form values
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    // Show loading state
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline-block';
    submitBtn.disabled = true;
    
    try {
        const data = await apiRequest('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        
        // Store token and user data
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        showToast('Login successful!', 'success');
        
        // Close modal and redirect
        closeLoginModal();
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 500);
        
    } catch (error) {
        showError('loginError', error.message);
    } finally {
        // Reset button state
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
        submitBtn.disabled = false;
    }
}

async function handleSignup(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoader = submitBtn.querySelector('.btn-loader');
    
    // Get form values
    const formData = {
        email: document.getElementById('signupEmail').value,
        password: document.getElementById('signupPassword').value,
        full_name: document.getElementById('signupName').value,
        age: parseInt(document.getElementById('signupAge').value) || null,
        salary: parseFloat(document.getElementById('signupSalary').value) || null,
        phone: document.getElementById('signupPhone').value || null
    };
    
    // Show loading state
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline-block';
    submitBtn.disabled = true;
    
    try {
        const data = await apiRequest('/auth/register', {
            method: 'POST',
            body: JSON.stringify(formData)
        });
        
        // Store token and user data
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        showToast('Account created successfully!', 'success');
        
        // Close modal and redirect
        closeSignupModal();
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 500);
        
    } catch (error) {
        showError('signupError', error.message);
    } finally {
        // Reset button state
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
        submitBtn.disabled = false;
    }
}

async function handleGoogleLogin() {
    // Placeholder for Google OAuth
    // In production, you would implement Google Sign-In SDK
    
    showToast('Google Sign-In will be available soon', 'error');
    
    // Example implementation:
    /*
    try {
        const googleUser = await window.gapi.auth2.getAuthInstance().signIn();
        const profile = googleUser.getBasicProfile();
        
        const data = await apiRequest('/auth/google', {
            method: 'POST',
            body: JSON.stringify({
                google_id: profile.getId(),
                email: profile.getEmail(),
                full_name: profile.getName()
            })
        });
        
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        closeLoginModal();
        window.location.href = 'dashboard.html';
        
    } catch (error) {
        showToast('Google login failed', 'error');
    }
    */
}

async function handleGoogleSignup() {
    // Same as handleGoogleLogin
    handleGoogleLogin();
}

function handleLogout() {
    // Clear local storage
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    
    showToast('Logged out successfully', 'success');
    
    // Redirect to home page
    setTimeout(() => {
        window.location.href = 'index.html';
    }, 500);
}

// ========== Auth Guard ==========
function requireAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'index.html';
        return false;
    }
    return true;
}

// ========== Get Current User ==========
function getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

function getAuthToken() {
    return localStorage.getItem('token');
}