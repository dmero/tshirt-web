// static/js/cart.js

// Cart functionality
let cartOpen = false;

// Initialize cart when page loads
document.addEventListener('DOMContentLoaded', function() {
    updateCartCount();
    loadCartItems();
});

// Toggle cart sidebar
function toggleCart() {
    const cartSidebar = document.getElementById('cart-sidebar');
    const cartOverlay = document.getElementById('cart-overlay');

    if (!cartOpen) {
        cartSidebar.inert = false;
        cartSidebar.setAttribute('aria-hidden', 'false');
        document.querySelector('.cart-btn').setAttribute('aria-expanded', 'true');
        cartSidebar.classList.add('active');
        cartOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
        cartOpen = true;
        cartSidebar.querySelector('.close-cart').focus();
        loadCartItems(); // Refresh cart items when opening
    } else {
        cartSidebar.classList.remove('active');
        cartOverlay.classList.remove('active');
        document.body.style.overflow = 'auto';
        cartOpen = false;
        cartSidebar.inert = true;
        cartSidebar.setAttribute('aria-hidden', 'true');
        document.querySelector('.cart-btn').setAttribute('aria-expanded', 'false');
        document.querySelector('.cart-btn').focus();
    }
}

// Toggle mobile menu
function toggleMenu() {
    const navMenu = document.querySelector('.nav-menu');
    const menuToggle = document.querySelector('.menu-toggle');
    const mobileOverlay = document.getElementById('mobile-menu-overlay');
    const body = document.body;

    navMenu.classList.toggle('active');
    menuToggle.setAttribute('aria-expanded', navMenu.classList.contains('active'));
    menuToggle.classList.toggle('active');

    if (mobileOverlay) {
        mobileOverlay.classList.toggle('active');
    }

    // Prevent body scroll when menu is open on mobile
    if (navMenu.classList.contains('active')) {
        body.style.overflow = 'hidden';
    } else {
        body.style.overflow = 'auto';
    }
}

// Close mobile menu when clicking outside
document.addEventListener('click', function(event) {
    const navMenu = document.querySelector('.nav-menu');
    const menuToggle = document.querySelector('.menu-toggle');

    if (navMenu && menuToggle) {
        const isClickInsideMenu = navMenu.contains(event.target);
        const isClickOnToggle = menuToggle.contains(event.target);

        if (!isClickInsideMenu && !isClickOnToggle && navMenu.classList.contains('active')) {
            toggleMenu();
        }
    }
});

// Close mobile menu when clicking on overlay
document.addEventListener('DOMContentLoaded', function() {
    const mobileOverlay = document.getElementById('mobile-menu-overlay');
    if (mobileOverlay) {
        mobileOverlay.addEventListener('click', toggleMenu);
    }
});

// Update cart count in navigation
function updateCartCount() {
    fetch('/cart/data/')
        .then(response => response.json())
        .then(data => {
            const cartCount = document.getElementById('cart-count');
            if (cartCount) {
                cartCount.textContent = data.total_items || 0;

                // Hide count if zero
                if (data.total_items === 0) {
                    cartCount.style.display = 'none';
                } else {
                    cartCount.style.display = 'block';
                }
            }
        })
        .catch(error => {
            console.error('Error updating cart count:', error);
        });
}

// Load cart items into sidebar
function loadCartItems() {
    fetch('/cart/data/')
        .then(response => response.json())
        .then(data => {

            const cartItemsContainer = document.getElementById('cart-items');
            const emptyCart = document.getElementById('empty-cart');
            const cartFooter = document.getElementById('cart-footer');
            const cartTotal = document.getElementById('cart-total');

            if (data.items && data.items.length > 0) {
                // Hide empty cart message
                if (emptyCart) emptyCart.style.display = 'none';
                if (cartFooter) cartFooter.style.display = 'block';

                // Build cart items HTML - keep empty cart div and add items after it
                let cartHTML = `
                    <div class="empty-cart" id="empty-cart" style="display: none;">
                        <i class="fas fa-shopping-cart"></i>
                        <p>Your bag is empty</p>
                    </div>
                `;

                data.items.forEach(item => {
                    cartHTML += `
                        <div class="modern-sidebar-item" data-item-id="${item.id}">
                            <div class="sidebar-item-image">
                                <img src="${escapeHTML(item.product_image || '/static/images/placeholder.svg')}"
                                     alt="${escapeHTML(item.product_name)}">
                            </div>
                            <div class="sidebar-item-details">
                                <h4 class="sidebar-item-name">${escapeHTML(item.product_name)}</h4>
                                <span class="sidebar-item-size">
                                    <i class="fas fa-ruler"></i> ${escapeHTML(item.size)}
                                </span>
                                <span class="sidebar-item-price">$${item.price.toFixed(2)}</span>
                            </div>
                            <div class="sidebar-item-actions">
                                <div class="sidebar-qty-controls">
                                    <button class="sidebar-qty-btn" aria-label="Decrease quantity" onclick="updateCartQuantity(${item.id}, ${item.quantity - 1})">
                                        <i class="fas fa-minus"></i>
                                    </button>
                                    <span class="sidebar-qty">${item.quantity}</span>
                                    <button class="sidebar-qty-btn" aria-label="Increase quantity" onclick="updateCartQuantity(${item.id}, ${item.quantity + 1})">
                                        <i class="fas fa-plus"></i>
                                    </button>
                                </div>
                                <button class="sidebar-remove-btn" onclick="removeFromCartSidebar(${item.id})" title="Remove">
                                    <i class="fas fa-trash-alt"></i>
                                </button>
                            </div>
                        </div>
                    `;
                });

                if (cartItemsContainer) {
                    cartItemsContainer.innerHTML = cartHTML;
                }
                if (cartTotal) {
                    cartTotal.textContent = data.total_price.toFixed(2);
                }

            } else {
                // Show empty cart message
                if (cartItemsContainer) {
                    cartItemsContainer.innerHTML = `
                        <div class="empty-cart" id="empty-cart">
                            <i class="fas fa-shopping-cart"></i>
                            <p>Your bag is empty</p>
                        </div>
                    `;
                }
                if (cartFooter) cartFooter.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error loading cart items:', error);
        });
}

// Update item quantity in cart
function updateCartQuantity(itemId, newQuantity) {
    if (newQuantity < 1) {
        removeFromCartSidebar(itemId);
        return;
    }

    const data = {
        item_id: itemId,
        quantity: newQuantity
    };

    fetch('/cart/update/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartCount();
            loadCartItems();
        } else {
            showNotification(data.message || 'Error updating cart', 'error');
        }
    })
    .catch(error => {
        console.error('Error updating cart:', error);
        showNotification('Error updating cart', 'error');
    });
}

// Remove item from cart (sidebar)
function removeFromCartSidebar(itemId) {
    const data = {
        item_id: itemId
    };

    fetch('/cart/remove/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartCount();
            loadCartItems();
            showNotification('Item removed from cart', 'success');
        } else {
            showNotification('Error removing item', 'error');
        }
    })
    .catch(error => {
        console.error('Error removing item:', error);
        showNotification('Error removing item', 'error');
    });
}

// Cart page functions
function updateCartItemQuantity(itemId, newQuantity) {
    if (newQuantity < 1) {
        removeCartItem(itemId);
        return;
    }

    const data = {
        item_id: itemId,
        quantity: newQuantity
    };

    // Show loading state
    const cartItem = document.querySelector(`[data-item-id="${itemId}"]`);
    if (cartItem) {
        cartItem.classList.add('loading');
    }

    fetch('/cart/update/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Reload the page to update cart display
            window.location.reload();
        } else {
            showNotification('Error updating cart', 'error');
            if (cartItem) {
                cartItem.classList.remove('loading');
            }
        }
    })
    .catch(error => {
        console.error('Error updating cart:', error);
        showNotification('Error updating cart', 'error');
        if (cartItem) {
            cartItem.classList.remove('loading');
        }
    });
}

// Remove item from cart (cart page)
function removeCartItem(itemId) {
    if (!confirm('Are you sure you want to remove this item?')) {
        return;
    }

    const data = {
        item_id: itemId
    };

    const cartItem = document.querySelector(`[data-item-id="${itemId}"]`);
    if (cartItem) {
        cartItem.classList.add('loading');
    }

    fetch('/cart/remove/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove item from DOM with animation
            if (cartItem) {
                cartItem.style.opacity = '0';
                cartItem.style.transform = 'translateX(-100%)';
                setTimeout(() => {
                    window.location.reload();
                }, 300);
            }
            showNotification('Item removed from cart', 'success');
        } else {
            showNotification('Error removing item', 'error');
            if (cartItem) {
                cartItem.classList.remove('loading');
            }
        }
    })
    .catch(error => {
        console.error('Error removing item:', error);
        showNotification('Error removing item', 'error');
        if (cartItem) {
            cartItem.classList.remove('loading');
        }
    });
}

// Navigate to checkout
function goToCheckout() {
    window.location.href = '/checkout/';
}

// Add to cart from product page
function addToCart(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    // Validate form
    const size = formData.get('size');
    const quantity = formData.get('quantity');

    if (!size) {
        showNotification('Please select a size', 'error');
        return;
    }

    if (!quantity || quantity < 1) {
        showNotification('Please select a valid quantity', 'error');
        return;
    }

    const data = {
        product_id: formData.get('product_id'),
        size: size,
        quantity: parseInt(quantity)
    };

    // Show loading state
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
    submitBtn.disabled = true;

    fetch('/cart/add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            updateCartCount();
            loadCartItems(); // Refresh cart sidebar

            // Auto-open cart sidebar to show the added item
            setTimeout(() => {
                if (!cartOpen) toggleCart();
            }, 500);

            // Reset form
            form.reset();
            const sizeSelect = form.querySelector('select[name="size"]');
            const hiddenSize = form.querySelector('input[name="size"][type="hidden"]');
            if (sizeSelect) sizeSelect.selectedIndex = 0;
            if (hiddenSize) hiddenSize.value = '';
            form.querySelector('input[name="quantity"]').value = 1;

            // Reset size button selection if using button-based size selector
            const sizeButtons = form.querySelectorAll('.size-btn');
            sizeButtons.forEach(btn => { btn.classList.remove('selected'); btn.setAttribute('aria-pressed', 'false'); });

        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error adding to cart:', error);
        showNotification('Error adding item to cart', 'error');
    })
    .finally(() => {
        // Reset button state
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    });
}

// Show notification
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());

    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.setAttribute('role', 'status');

    // Add to page
    document.body.appendChild(notification);

    // Trigger show animation
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);

    // Auto hide after 4 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }, 4000);
}

// Get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Close cart when clicking outside
document.addEventListener('click', function(event) {
    const cartSidebar = document.getElementById('cart-sidebar');
    const cartBtn = document.querySelector('.cart-btn');

    if (cartOpen && !cartSidebar.contains(event.target) && !cartBtn.contains(event.target)) {
        toggleCart();
    }
});

// Handle escape key to close cart
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape' && cartOpen) {
        toggleCart();
    }
});

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const href = this.getAttribute('href');
        const target = href.length > 1 ? document.getElementById(href.slice(1)) : null;
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Form validation enhancements
function enhanceFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, select, textarea');

        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                if (this.hasAttribute('required') && !this.value.trim()) {
                    this.classList.add('error');
                } else {
                    this.classList.remove('error');
                }
            });

            input.addEventListener('input', function() {
                if (this.classList.contains('error') && this.value.trim()) {
                    this.classList.remove('error');
                }
            });
        });
    });
}

// Initialize form validation when DOM is ready
document.addEventListener('DOMContentLoaded', enhanceFormValidation);

// Lazy loading for images
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');

    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback for older browsers
        images.forEach(img => {
            img.src = img.dataset.src;
        });
    }
}

// Initialize lazy loading
document.addEventListener('DOMContentLoaded', initLazyLoading);

// Search functionality (if implemented)
function initSearch() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        let searchTimeout;

        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();

            if (query.length > 2) {
                searchTimeout = setTimeout(() => {
                    performSearch(query);
                }, 300);
            }
        });
    }
}

function performSearch(query) {
    // Implement search functionality
    console.log('Searching for:', query);
    // This would typically make an AJAX request to search endpoint
}

// Initialize search
document.addEventListener('DOMContentLoaded', initSearch);

// Back to top button
function initBackToTop() {
    const backToTopBtn = document.createElement('button');
    backToTopBtn.innerHTML = '<i class="fas fa-chevron-up"></i>';
    backToTopBtn.className = 'back-to-top';
    backToTopBtn.setAttribute('aria-label', 'Back to top');
    backToTopBtn.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #007bff;
        color: white;
        border: none;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        cursor: pointer;
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s;
        z-index: 1000;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    `;

    document.body.appendChild(backToTopBtn);

    // Show/hide button based on scroll position
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            backToTopBtn.style.opacity = '1';
            backToTopBtn.style.visibility = 'visible';
        } else {
            backToTopBtn.style.opacity = '0';
            backToTopBtn.style.visibility = 'hidden';
        }
    });

    // Scroll to top when clicked
    backToTopBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Initialize back to top button
document.addEventListener('DOMContentLoaded', initBackToTop);

// Product image zoom (for product detail page)
function initImageZoom() {
    const productImage = document.querySelector('.main-image');
    if (productImage) {
        productImage.addEventListener('mouseover', function() {
            this.style.transform = 'scale(1.2)';
            this.style.cursor = 'zoom-in';
        });

        productImage.addEventListener('mouseout', function() {
            this.style.transform = 'scale(1)';
        });

        productImage.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = ((e.clientX - rect.left) / rect.width) * 100;
            const y = ((e.clientY - rect.top) / rect.height) * 100;
            this.style.transformOrigin = `${x}% ${y}%`;
        });
    }
}

// Initialize image zoom
document.addEventListener('DOMContentLoaded', initImageZoom);

function escapeHTML(value) {
    return String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
}
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape' && document.querySelector('.nav-menu.active')) toggleMenu();
    if (event.key !== 'Tab' || !cartOpen) return;
    const controls = Array.from(document.querySelectorAll('#cart-sidebar button, #cart-sidebar a[href]')).filter(el => el.offsetParent !== null && !el.disabled);
    if (!controls.length) return;
    const first = controls[0], last = controls[controls.length - 1];
    if (!document.getElementById('cart-sidebar').contains(document.activeElement)) { event.preventDefault(); first.focus(); }
    else if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
});
