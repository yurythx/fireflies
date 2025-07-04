/**
 * Config Admin Panel JavaScript
 * Handles all interactions, animations and responsive behavior
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize config page functionality
    initConfigPanel();
    
    // Initialize sidebar mobile toggle
    initSidebarMobile();
    
    // Initialize form interactions
    initFormInteractions();
    
    // Initialize animations
    initAnimations();
    
    // Initialize tooltips
    initTooltips();
    
    // Auto-close alerts
    initAutoCloseAlerts();
});

/**
 * Initialize main config panel functionality
 */
function initConfigPanel() {
    console.log('Config Admin Panel initialized');
    
    // Add config-specific classes to elements
    addConfigClasses();
    
    // Initialize page transitions
    initPageTransitions();
    
    // Initialize button interactions
    initButtonInteractions();
}

/**
 * Add config-specific classes to elements
 */
function addConfigClasses() {
    // Add config-btn class to all buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
        btn.classList.add('config-btn');
    });
    
    // Add config-card class to all cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.classList.add('config-card');
    });
    
    // Add config-content class to main content
    const content = document.querySelector('main, .config-content');
    if (content) {
        content.classList.add('config-content');
    }
}

/**
 * Initialize sidebar mobile functionality
 */
function initSidebarMobile() {
    const sidebarToggle = document.querySelector('[data-bs-target="#sidebar"]');
    const sidebar = document.querySelector('#sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            // Add show class for custom animations
            sidebar.classList.add('show');
        });
        
        // Handle sidebar close
        const closeButtons = document.querySelectorAll('[data-bs-dismiss="offcanvas"]');
        closeButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                sidebar.classList.remove('show');
            });
        });
    }
}

/**
 * Initialize form interactions
 */
function initFormInteractions() {
    // Form field focus animations
    const formControls = document.querySelectorAll('.form-control, .form-select');
    formControls.forEach(control => {
        control.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
            this.style.transform = 'translateY(-2px)';
        });

        control.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
            this.style.transform = 'translateY(0)';
        });
    });

    // Form submission loading states
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.classList.add('config-loading');
                submitBtn.disabled = true;

                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processando...';

                // Reset after 5 seconds if still loading
                setTimeout(() => {
                    submitBtn.classList.remove('config-loading');
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }, 5000);
            }
        });
    });
}

/**
 * Initialize page transitions
 */
function initPageTransitions() {
    // Smooth transitions for sidebar navigation
    const sidebarLinks = document.querySelectorAll('.sidebar .nav-link');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Don't prevent default, but add transition effect
            const mainContent = document.querySelector('.config-main-content, main');
            if (mainContent) {
                mainContent.classList.add('page-transition');

                // Remove transition class after navigation
                setTimeout(() => {
                    mainContent.classList.remove('page-transition');
                }, 300);
            }
        });
    });
}

/**
 * Initialize button interactions
 */
function initButtonInteractions() {
    // Enhanced button interactions
    const configBtns = document.querySelectorAll('.btn');
    configBtns.forEach(btn => {
        btn.classList.add('config-btn');

        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });

        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
        
        // Add ripple effect
        btn.addEventListener('click', function(e) {
            createRippleEffect(e);
        });
    });
}

/**
 * Initialize animations
 */
function initAnimations() {
    // Animate main content
    const content = document.querySelector('.config-content, main');
    if (content) {
        content.classList.add('config-content');
        setTimeout(() => {
            content.classList.add('loaded');
        }, 100);
    }

    // Animate cards with stagger effect
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.classList.add('config-card');
        setTimeout(() => {
            card.classList.add('animate-in');
        }, 150 + (index * 100));
    });

    // Animate statistics cards
    const statCards = document.querySelectorAll('.border-left-primary, .border-left-success, .border-left-warning, .border-left-info');
    statCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';

        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 200 + (index * 150));
    });

    // Animate table rows
    const tableRows = document.querySelectorAll('table tbody tr');
    tableRows.forEach((row, index) => {
        row.style.opacity = '0';
        row.style.transform = 'translateX(-20px)';
        row.style.transition = 'opacity 0.4s ease, transform 0.4s ease';

        setTimeout(() => {
            row.style.opacity = '1';
            row.style.transform = 'translateX(0)';
        }, 300 + (index * 50));
    });
}

/**
 * Initialize tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize auto-close alerts
 */
function initAutoCloseAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-danger)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

/**
 * Create ripple effect on button click
 */
function createRippleEffect(e) {
    const button = e.target.classList.contains('btn') ? e.target : e.target.closest('.btn');
    if (!button) return;

    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;

    const ripple = document.createElement('span');
    ripple.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        left: ${x}px;
        top: ${y}px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        transform: scale(0);
        animation: ripple 0.6s linear;
        pointer-events: none;
        z-index: 1;
    `;

    button.style.position = 'relative';
    button.style.overflow = 'hidden';
    button.appendChild(ripple);

    setTimeout(() => {
        ripple.remove();
    }, 600);
}

/**
 * Page transition handler for config navigation
 */
function handleConfigNavigation(url) {
    const mainContent = document.querySelector('main');
    if (mainContent) {
        // Add exit animation
        mainContent.style.opacity = '0.7';
        mainContent.style.transform = 'translateY(10px)';

        setTimeout(() => {
            window.location.href = url;
        }, 200);
    } else {
        window.location.href = url;
    }
}

/**
 * Show loading state for config operations
 */
function showConfigLoading(element) {
    if (element) {
        element.classList.add('config-loading');
        element.disabled = true;
        
        const originalText = element.innerHTML;
        element.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processando...';
        
        return {
            hide: function() {
                element.classList.remove('config-loading');
                element.disabled = false;
                element.innerHTML = originalText;
            }
        };
    }
}

/**
 * Add ripple animation CSS
 */
function addRippleCSS() {
    if (!document.querySelector('#ripple-css')) {
        const rippleStyle = document.createElement('style');
        rippleStyle.id = 'ripple-css';
        rippleStyle.textContent = `
            @keyframes ripple {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(rippleStyle);
    }
}

// Add ripple CSS on load
addRippleCSS();

// Export functions for global use
window.ConfigAdmin = {
    handleNavigation: handleConfigNavigation,
    showLoading: showConfigLoading,
    initPanel: initConfigPanel
}; 