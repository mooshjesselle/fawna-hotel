// Define categories globally for food menu filtering
const categories = ["All", "Rice Meals", "Burgers", "Desserts", "Beverages"];

// Form validation
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Initialize date pickers
    const dateInputs = document.querySelectorAll('input[type="date"]');
    const today = new Date().toISOString().split('T')[0];
    const oneYearFromNow = new Date();
    oneYearFromNow.setFullYear(oneYearFromNow.getFullYear() + 1);
    const maxDate = oneYearFromNow.toISOString().split('T')[0];
    
    dateInputs.forEach(input => {
        if (input.id === 'check_in') {
            input.min = today;
            input.max = maxDate;
        } else if (input.id === 'check_out') {
            input.min = today;
            input.max = maxDate;
        }
    });

    // Check-out date validation
    const checkInInput = document.getElementById('check_in');
    const checkOutInput = document.getElementById('check_out');
    
    if (checkInInput && checkOutInput) {
        checkInInput.addEventListener('change', function() {
            checkOutInput.min = this.value;
            
            // If check-out date is before check-in date, update it
            if (checkOutInput.value && new Date(checkOutInput.value) < new Date(this.value)) {
                checkOutInput.value = this.value;
            }
            
            // If check-out date is beyond one year from now, update it
            if (checkOutInput.value && new Date(checkOutInput.value) > oneYearFromNow) {
                checkOutInput.value = maxDate;
            }
        });
        
        checkOutInput.addEventListener('change', function() {
            // If check-out date is beyond one year from check-in, limit it
            const selectedCheckIn = new Date(checkInInput.value || today);
            const maxCheckOut = new Date(selectedCheckIn);
            maxCheckOut.setFullYear(maxCheckOut.getFullYear() + 1);
            
            if (new Date(this.value) > maxCheckOut) {
                this.value = maxCheckOut.toISOString().split('T')[0];
            }
        });
    }

    // Food Menu Modal logic
    const viewFoodMenuBtn = document.getElementById('view-food-menu-btn');
    const fabBtn = document.getElementById('view-food-menu-btn-fab');
    const foodMenuModal = document.getElementById('foodMenuModal');
    const foodMenuContent = document.getElementById('food-menu-content');
    let bsFoodMenuModal = null;
    if (foodMenuModal && typeof bootstrap !== 'undefined') {
        bsFoodMenuModal = new bootstrap.Modal(foodMenuModal);
    }
    function showFoodMenuModal(skipCleanup = false) {
        if (!foodMenuContent) return;
        
        // Ensure Your Orders button events are always properly set up
        const ensureYourOrdersButtonAlways = () => {
            const setupButton = () => {
                const yourOrdersBtn = document.getElementById('yourOrdersCatBtn');
                if (yourOrdersBtn) {
                    console.log('🔧 Ensuring Your Orders button events are properly attached...');
                    
                    // Remove any existing event listeners
                    yourOrdersBtn.removeEventListener('click', handleYourOrdersClick);
                    yourOrdersBtn.removeEventListener('click', handleYourOrdersClickDirect);
                    
                    // Clear any existing onclick handlers
                    yourOrdersBtn.onclick = null;
                    
                    // Add event listeners
                    yourOrdersBtn.addEventListener('click', handleYourOrdersClickDirect);
                                                    yourOrdersBtn.onclick = function(e) {
                                    e.preventDefault();
                                    e.stopPropagation();
                                    console.log('Your Orders button clicked (from ensureYourOrdersButtonAlways)!');
                                    
                                    // Remove 'active' from all category buttons and cart button
                                    document.querySelectorAll('.food-cat-btn').forEach(btn => {
                                        btn.classList.remove('active');
                                        console.log('Removed active from:', btn.textContent || btn.id);
                                    });
                                    
                                    // Set 'active' on this button specifically
                                    this.classList.add('active');
                                    console.log('Added active to Your Orders button (ensureYourOrdersButtonAlways)');
                                    
                                    // Load order history
                                    loadYourOrders();
                                };
                    
                    console.log('✅ Your Orders button events successfully attached');
                    return true;
                }
                return false;
            };
            
            // Try immediate setup
            if (!setupButton()) {
                // If not found, retry with multiple attempts
                let attempts = 0;
                const maxAttempts = 10;
                const retrySetup = () => {
                    attempts++;
                    console.log(`🔄 Attempt ${attempts} to find Your Orders button...`);
                    
                    if (setupButton()) {
                        console.log('✅ Your Orders button setup successful!');
                        return;
                    }
                    
                    if (attempts < maxAttempts) {
                        setTimeout(retrySetup, 100);
                    } else {
                        console.error('❌ Failed to find Your Orders button after multiple attempts');
                    }
                };
                
                setTimeout(retrySetup, 50);
            }
        };
        
        // Debug cart state when modal opens
        console.log('=== FOOD MENU MODAL OPENING ===');
        console.log('Cart state when modal opens:', cart);
        console.log('Cart length:', cart.length);
        console.log('Total items in cart:', cart.reduce((sum, item) => sum + item.quantity, 0));
        console.log('LocalStorage foodCart:', localStorage.getItem('foodCart'));
        console.log('================================');
        
        // Check if modal is already open
            const modalEl = document.getElementById('foodMenuModal');
        const isModalAlreadyOpen = modalEl && modalEl.classList.contains('show');
        
        // Ensure the modal element is attached directly to <body> to avoid stacking/backdrop issues
            if (modalEl && modalEl.parentNode !== document.body) {
                document.body.appendChild(modalEl);
            }
        
        // Only clean backdrop if we're opening a new modal and not skipping cleanup
        if (!isModalAlreadyOpen && !skipCleanup) {
            // Pre-clean any lingering modal/backdrop/body state before showing
            document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
            document.body.classList.remove('modal-open');
            document.body.style.removeProperty('padding-right');
            document.body.style.removeProperty('overflow');
        }

            foodMenuContent.innerHTML = '<div class="food-menu-content-card"><div class="text-center text-muted"><i class="fas fa-spinner fa-spin me-2"></i>Loading menu...</div></div>';
            
            // Ensure cart is loaded from storage before fetching menu
            loadCartFromStorage();
            
            console.log('[DEBUG] Fetching food menu...');
            fetch('/api/food-menu')
                .then(response => response.json())
                .then(data => {
                    console.log('[DEBUG] /api/food-menu response:', data);
                    let html = '';
                if (data.error === 'Food service is currently unavailable. Please try again later.') {
                    html = `<div class='food-unavailable-message' style="background:#e7d7ce;color:#6D4C41;font-size:1.6rem;padding:32px 16px;margin:0 auto;border-radius:16px;width:100%;min-height:120px;display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 4px 24px rgba(0,0,0,0.10);text-align:center;">
        <i class='fas fa-utensils fa-2x mb-3'></i>
        <span style='font-weight:700;'>Food service is unavailable.</span>
    </div>`;
                } else if (data.error) {
                        html = `<div class='alert alert-danger'>Error: ${data.error}</div>`;
                        if (data.raw_response) {
                            html += `<pre style="max-height:200px;overflow:auto;background:#f8f9fa;border:1px solid #ccc;padding:8px;">${data.raw_response}</pre>`;
                        }
                    } else if (Array.isArray(data.menu)) {
                        html = '<ul class="list-group">';
                        data.menu.forEach(item => {
                            html += `<li class="list-group-item"><strong>${item.name}</strong>: ₱${item.price} <br>${item.description || ''}</li>`;
                        });
                        html += '</ul>';
                    } else if (Array.isArray(data)) {
                        // Add a style block for category buttons and responsive grid
                        const catStyle = document.createElement('style');
                        catStyle.innerHTML = `
                        .food-cat-btn {
                          margin: 0 6px 10px 0 !important;
                          border-radius: 20px !important;
                          font-weight: 600;
                          min-width: 110px;
                          background: #fff;
                          color: #6D4C41;
                          border: 2px solid #6D4C41;
                          transition: background 0.2s, color 0.2s, border 0.2s;
                        }
                        .food-cat-btn.active, .food-cat-btn:focus {
                          background: #6D4C41 !important;
                          color: #fff !important;
                          border: 2px solid #6D4C41 !important;
                          outline: none;
                        }
                        .food-cat-btn:hover {
                          background: #e7d7ce !important;
                          color: #6D4C41 !important;
                          border: 2px solid #6D4C41 !important;
                        }
                        
                        /* Specific styling for Your Orders button to prevent hover conflicts */
                        #yourOrdersCatBtn {
                          margin-right: 12px !important;
                          position: relative !important;
                          z-index: 10 !important;
                          pointer-events: auto !important;
                        }
                        
                        #yourOrdersCatBtn:hover {
                          background: #e7d7ce !important;
                          color: #6D4C41 !important;
                          border: 2px solid #6D4C41 !important;
                          z-index: 15 !important;
                        }
                        
                        /* Specific styling for cart button */
                        #viewCartBtn {
                          position: relative !important;
                          z-index: 5 !important;
                          pointer-events: auto !important;
                        }
                        
                        #viewCartBtn:hover {
                          background: #e7d7ce !important;
                          color: #6D4C41 !important;
                          border: 2px solid #6D4C41 !important;
                          z-index: 8 !important;
                        }
                        
                        /* Ensure buttons don't overlap or interfere with each other */
                        .food-cat-btn {
                          margin: 0 6px 10px 0 !important;
                          border-radius: 20px !important;
                          font-weight: 600;
                          min-width: 110px;
                          background: #fff;
                          color: #6D4C41;
                          border: 2px solid #6D4C41;
                          transition: background 0.2s, color 0.2s, border 0.2s;
                          position: relative !important;
                          pointer-events: auto !important;
                          isolation: isolate !important;
                        }
                        
                        /* Container for Your Orders and Cart buttons */
                        .food-cat-btn-container {
                          display: inline-block !important;
                          margin-left: 20px !important;
                          position: relative !important;
                          z-index: 1 !important;
                        }
                        
                        .food-menu-grid {
                          max-width: 1400px;
                          margin: 0 auto;
                        }
                        @media (max-width: 1200px) {
                          .food-menu-grid {
                            grid-template-columns: repeat(3, 1fr) !important;
                          }
                        }
                        @media (max-width: 800px) {
                          .food-menu-grid {
                            grid-template-columns: repeat(1, 1fr) !important;
                          }
                        }
                        `;
                        document.head.appendChild(catStyle);
                        html = '<div style="margin-bottom:16px;text-align:center;">';
                        categories.forEach((cat, idx) => {
                            html += `<button class="food-cat-btn${idx === 0 ? ' active' : ''}" data-cat="${cat}">${cat}</button> `;
                        });
                        // Add 'Your Orders' button and cart button in separate container to prevent overlap
                        html += `<div class="food-cat-btn-container">`;
                        html += `<button class="food-cat-btn" id="yourOrdersCatBtn" style="margin-right: 15px;">Your Orders</button>`;
                        html += `<button class="food-cat-btn" id="viewCartBtn" style="position:relative;">
                            <i class="fas fa-shopping-cart"></i> Cart
                            <span id="cartItemCount" style="position:absolute;top:-8px;right:-8px;background:#ff4757;color:white;border-radius:50%;width:20px;height:20px;font-size:12px;display:flex;align-items:center;justify-content:center;font-weight:bold;">0</span>
                        </button>`;
                        html += `</div>`;
                        html += '</div>';
                        html += '<div class="food-menu-grid" style="display:grid;grid-template-columns:repeat(5,1fr);gap:16px;max-width:1400px;margin:0 auto;">';
                        data.forEach(item => {
                            const itemCat = item.category || "Other";
                            // Fix image URL to use correct IP address
                            const correctedImageUrl = item.image ? item.image.replace(/192\.168\.107\.226/g, window.FOOD_SERVICE_IP || '192.168.1.12') : item.image;
                            html += `
                            <div class="food-menu-item" data-category="${itemCat}" style="background:#fff;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.08);padding:16px;display:flex;flex-direction:column;align-items:center;min-height:340px;height:100%;justify-content:space-between;transition:all 0.3s ease;border:1px solid #f0f0f0;">
                                <img src="${correctedImageUrl}" alt="${item.name}" style="width:150px;height:150px;object-fit:cover;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,0.1);">
                                <div class="cart-controls" style="display:flex;align-items:center;gap:8px;margin:8px 0;">
                                    <div class="quantity-controls" style="display:flex;align-items:center;gap:8px;background:#f8f9fa;border-radius:20px;padding:4px;">
                                        <button class="quantity-btn minus-btn" data-id="${item.id}" style="background:#6D4C41;color:white;border:none;border-radius:50%;width:28px;height:28px;display:flex;align-items:center;justify-content:center;cursor:pointer;font-weight:bold;font-size:16px;">-</button>
                                        <span class="quantity-display" data-id="${item.id}" style="min-width:30px;text-align:center;font-weight:600;font-size:14px;color:#6D4C41;">1</span>
                                        <button class="quantity-btn plus-btn" data-id="${item.id}" style="background:#6D4C41;color:white;border:none;border-radius:50%;width:28px;height:28px;display:flex;align-items:center;justify-content:center;cursor:pointer;font-weight:bold;font-size:16px;">+</button>
                                    </div>
                                    <button class="add-to-cart-btn" data-id="${item.id}" data-name="${item.name}" data-price="${item.price}" data-image="${correctedImageUrl}" data-description="${item.description || ''}" style="background:#8b5e3b;color:white;border:none;border-radius:20px;padding:8px 16px;font-size:12px;font-weight:600;cursor:pointer;transition:all 0.3s ease;">Add to Cart</button>
                                </div>
                                <div style="margin-top:12px;text-align:center;flex:1;display:flex;flex-direction:column;justify-content:space-between;width:100%;">
                                    <div style="margin-bottom:8px;">
                                        <strong style="font-size:16px;color:#4e342e;display:block;margin-bottom:4px;">${item.name}</strong>
                                        <span style="font-size:18px;font-weight:600;color:#8b5e3b;">₱${item.price}</span>
                                    </div>
                                    <span style="color:#666;font-size:14px;line-height:1.4;">${item.description || ''}</span>
                                </div>
                            </div>`;
                        });
                        html += '</div>';
                    } else {
                        html = '<div class="text-muted">No menu available.</div>';
                    }
                    foodMenuContent.innerHTML = `<div class='food-menu-content-card'>${html}</div>`;
                    
                    // Ensure Your Orders button has proper event handling - IMMEDIATE setup
                    const setupYourOrdersButton = () => {
                        const yourOrdersBtn = document.getElementById('yourOrdersCatBtn');
                        if (yourOrdersBtn) {
                            console.log('✅ Your Orders button found, setting up events immediately');
                            
                            // Remove any existing event listeners to prevent conflicts
                            yourOrdersBtn.removeEventListener('click', handleYourOrdersClick);
                            yourOrdersBtn.removeEventListener('click', handleYourOrdersClickDirect);
                            
                            // Clear any existing onclick handlers
                            yourOrdersBtn.onclick = null;
                            
                            // Add event listeners
                            yourOrdersBtn.addEventListener('click', handleYourOrdersClickDirect);
                            yourOrdersBtn.onclick = function(e) {
                                e.preventDefault();
                                e.stopPropagation();
                                console.log('Your Orders button clicked (immediate setup)!');
                                
                                // Remove 'active' from all category buttons and cart button
                                document.querySelectorAll('.food-cat-btn').forEach(btn => {
                                    btn.classList.remove('active');
                                    console.log('Removed active from:', btn.textContent || btn.id);
                                });
                                
                                // Set 'active' on this button specifically
                                this.classList.add('active');
                                console.log('Added active to Your Orders button (immediate setup)');
                                
                                // Load order history
                                loadYourOrders();
                            };
                            
                            console.log('✅ Your Orders button events successfully attached');
                            return true; // Success
                        }
                        return false; // Button not found
                    };
                    
                    // Try immediate setup first
                    if (!setupYourOrdersButton()) {
                        // If immediate setup fails, try with delays
                        setTimeout(() => {
                            if (!setupYourOrdersButton()) {
                                setTimeout(() => {
                                    setupYourOrdersButton();
                                }, 100);
                            }
                        }, 50);
                    }
                    
                    // Add event listeners for quantity controls
                    setTimeout(() => {
                        addFoodMenuQuantityEventListeners();
                        updateFoodMenuQuantityDisplays();
                    }, 100);
                    
                    // If modal is already open, ensure backdrop is properly maintained
                    if (isModalAlreadyOpen) {
                        if (typeof ensureModalBackdrop === 'function') {
                            ensureModalBackdrop();
                        } else {
                            // Fallback if helper function is not available
                            let backdrop = document.querySelector('.modal-backdrop');
                            if (!backdrop) {
                                backdrop = document.createElement('div');
                                backdrop.className = 'modal-backdrop fade show';
                                document.body.appendChild(backdrop);
                            }
                            document.body.classList.add('modal-open');
                        }
                    }
                    
                    // The cart count badge is already created with the correct count in the HTML above
                    // No need to call updateCartCountBadge() here as it might override the correct value
                    console.log('✅ Food menu modal loaded with cart count badge:', cart.length);
                    
                    // Fallback: Update cart count badge after a short delay to ensure it's visible
                    setTimeout(() => {
                        const cartItemCount = document.getElementById('cartItemCount');
                        if (cartItemCount) {
                            const actualCartCount = cart.length;
                            cartItemCount.textContent = actualCartCount;
                            cartItemCount.style.display = actualCartCount > 0 ? 'flex' : 'none';
                            console.log('✅ Fallback: Updated cart count badge to:', actualCartCount);
                        }
                    }, 50);
                })
                .catch(err => {
                    foodMenuContent.innerHTML = `<div class='food-menu-content-card'><div class='alert alert-danger'>Failed to load menu: ${err}</div></div>`;
                });
            
            // Only show modal if it's not already open
            if (!isModalAlreadyOpen && typeof bootstrap !== 'undefined') {
                const instance = bootstrap.Modal.getOrCreateInstance(document.getElementById('foodMenuModal'), { backdrop: true, keyboard: true, focus: true });
                instance.show();
            }
            
            // Ensure Your Orders button events are always properly set up
            ensureYourOrdersButtonAlways();
            
            // Set up MutationObserver to watch for Your Orders button being added
            const setupMutationObserver = () => {
                const foodMenuContent = document.getElementById('food-menu-content');
                if (!foodMenuContent) return;
                
                // Create observer to watch for changes in the food menu content
                const observer = new MutationObserver((mutations) => {
                    mutations.forEach((mutation) => {
                        if (mutation.type === 'childList') {
                            // Check if Your Orders button was added
                            const yourOrdersBtn = document.getElementById('yourOrdersCatBtn');
                            if (yourOrdersBtn) {
                                console.log('🔍 MutationObserver detected Your Orders button, setting up events...');
                                
                                // Remove any existing event listeners
                                yourOrdersBtn.removeEventListener('click', handleYourOrdersClick);
                                yourOrdersBtn.removeEventListener('click', handleYourOrdersClickDirect);
                                yourOrdersBtn.onclick = null;
                                
                                // Add event listeners
                                yourOrdersBtn.addEventListener('click', handleYourOrdersClickDirect);
                                yourOrdersBtn.onclick = function(e) {
                                    e.preventDefault();
                                    e.stopPropagation();
                                    console.log('Your Orders button clicked (from MutationObserver)!');
                                    
                                    // Remove 'active' from all category buttons and cart button
                                    document.querySelectorAll('.food-cat-btn').forEach(btn => {
                                        btn.classList.remove('active');
                                        console.log('Removed active from:', btn.textContent || btn.id);
                                    });
                                    
                                    // Set 'active' on this button specifically
                                    this.classList.add('active');
                                    console.log('Added active to Your Orders button (MutationObserver)');
                                    
                                    // Load order history
                                    loadYourOrders();
                                };
                                
                                console.log('✅ Your Orders button events attached via MutationObserver');
                            }
                        }
                    });
                });
                
                // Start observing
                observer.observe(foodMenuContent, {
                    childList: true,
                    subtree: true
                });
                
                console.log('🔍 MutationObserver set up to watch for Your Orders button');
            };
            
            // Set up the observer
            setTimeout(setupMutationObserver, 100);
    }
    window.showFoodMenuModal = showFoodMenuModal;
    if (viewFoodMenuBtn) {
        viewFoodMenuBtn.addEventListener('click', showFoodMenuModal);
    }
    if (fabBtn) {
        fabBtn.addEventListener('click', showFoodMenuModal);
    }
});

// Fix: Remove lingering modal-backdrop and modal-open class when food menu modal is closed
const foodMenuModalEl = document.getElementById('foodMenuModal');
if (foodMenuModalEl) {
    // Always fetch and render menu when modal is shown
    foodMenuModalEl.addEventListener('show.bs.modal', function () {
        // Ensure the floating button is clickable
        const orderFoodBtn = document.getElementById('orderFoodBtn');
        if (orderFoodBtn) {
            orderFoodBtn.style.pointerEvents = 'auto';
            orderFoodBtn.style.opacity = '1';
        }
        
        // Ensure modal animations are properly set up
        if (typeof ensureModalAnimations === 'function') {
            ensureModalAnimations();
        }
        
        // Set up periodic backdrop check to ensure it stays visible
        this._backdropCheckInterval = setInterval(() => {
            if (this.classList.contains('show') && typeof monitorModalBackdrop === 'function') {
                monitorModalBackdrop();
            }
        }, 1000);
        
        // Ensure backdrop animation is smooth
        setTimeout(() => {
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) {
                backdrop.style.transition = 'opacity 0.15s linear';
            }
        }, 50);
        const foodMenuContent = document.getElementById('food-menu-content');
        if (foodMenuContent) {
            foodMenuContent.innerHTML = '<div class="food-menu-content-card"><div class="text-center text-muted"><i class="fas fa-spinner fa-spin me-2"></i>Loading menu...</div></div>';
            fetch('/api/food-menu')
                .then(response => response.json())
                .then(data => {
                    let html = '';
                    if (data.error === 'Food service is currently unavailable. Please try again later.') {
                        html = `<div class='food-unavailable-message' style="background:#e7d7ce;color:#6D4C41;font-size:1.6rem;padding:32px 16px;margin:0 auto;border-radius:16px;width:100%;min-height:120px;display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 4px 24px rgba(0,0,0,0.10);text-align:center;">
        <i class='fas fa-utensils fa-2x mb-3'></i>
        <span style='font-weight:700;'>Food service is unavailable.</span>
    </div>`;
                    } else if (data.error) {
                        html = `<div class='alert alert-danger'>Error: ${data.error}</div>`;
                        if (data.raw_response) {
                            html += `<pre style="max-height:200px;overflow:auto;background:#f8f9fa;border:1px solid #ccc;padding:8px;">${data.raw_response}</pre>`;
                        }
                    } else if (Array.isArray(data.menu)) {
                        html = '<ul class="list-group">';
                        data.menu.forEach(item => {
                            html += `<li class="list-group-item"><strong>${item.name}</strong>: ₱${item.price} <br>${item.description || ''}</li>`;
                        });
                        html += '</ul>';
                    } else if (Array.isArray(data)) {
                        // Add a style block for category buttons
                        const catStyle = document.createElement('style');
                        catStyle.innerHTML = `
                        .food-cat-btn {
                          margin: 0 6px 10px 0 !important;
                          border-radius: 20px !important;
                          font-weight: 600;
                          min-width: 110px;
                          background: #fff;
                          color: #6D4C41;
                          border: 2px solid #6D4C41;
                          transition: background 0.2s, color 0.2s, border 0.2s;
                        }
                        .food-cat-btn.active, .food-cat-btn:focus {
                          background: #6D4C41 !important;
                          color: #fff !important;
                          border: 2px solid #6D4C41 !important;
                          outline: none;
                        }
                        .food-cat-btn:hover {
                          background: #e7d7ce !important;
                          color: #6D4C41 !important;
                          border: 2px solid #6D4C41 !important;
                        }`;
                        document.head.appendChild(catStyle);
                        // When rendering category buttons, use only food-cat-btn class (no Bootstrap btn-outline-primary or btn-sm)
                        html = '<div style="margin-bottom:16px;text-align:center;">';
                        categories.forEach((cat, idx) => {
                            html += `<button class="food-cat-btn${idx === 0 ? ' active' : ''}" data-cat="${cat}">${cat}</button> `;
                        });
                        // Add 'Your Orders' button and cart button in line with categories
                        // Fix cart badge positioning to prevent overlapping in modal
                        // Calculate current cart count for the badge (number of unique items, not total quantity)
                        const currentCartCount = cart.length; // Changed from cart.reduce((sum, item) => sum + item.quantity, 0)
                        const badgeDisplay = currentCartCount > 0 ? 'flex' : 'none';
                        
                        console.log('=== CREATING CART COUNT BADGE ===');
                        console.log('Cart array when creating badge:', cart);
                        console.log('currentCartCount calculated (number of items):', currentCartCount);
                        console.log('badgeDisplay:', badgeDisplay);
                        console.log('Cart is array?', Array.isArray(cart));
                        console.log('Cart length:', cart.length);
                        console.log('====================================');
                        
                        html += `<button class="food-cat-btn" id="yourOrdersCatBtn">Your Orders</button>`;
                        html += `<button class="food-cat-btn" id="viewCartBtn" style="position:relative;padding-right:28px;">
                            <i class="fas fa-shopping-cart"></i> Cart
                            <span id="cartItemCount" style="position:absolute;top:-6px;right:6px;background:#ff4757;color:white;border-radius:50%;min-width:18px;height:18px;font-size:11px;display:${badgeDisplay};align-items:center;justify-content:center;font-weight:bold;border:2px solid #fff;box-shadow:0 2px 4px rgba(0,0,0,0.2);z-index:10;">${currentCartCount}</span>
                        </button>`;
                        html += '</div>';
                        html += '<div class="food-menu-grid" style="display:grid;grid-template-columns:repeat(5,1fr);gap:16px;">';
                        data.forEach(item => {
                            const itemCat = item.category || "Other";
                            // Fix image URL to use correct IP address
                            const correctedImageUrl = item.image ? item.image.replace(/192\.168\.107\.226/g, window.FOOD_SERVICE_IP || '192.168.1.12') : item.image;
                            html += `
                            <div class="food-menu-item" data-category="${itemCat}" style="background:#fff;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.08);padding:16px;display:flex;flex-direction:column;align-items:center;min-height:340px;height:100%;justify-content:space-between;transition:all 0.3s ease;border:1px solid #f0f0f0;">
                                <img src="${correctedImageUrl}" alt="${item.name}" style="width:150px;height:150px;object-fit:cover;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,0.1);">
                                <div class="cart-controls" style="display:flex;align-items:center;gap:8px;margin:8px 0;">
                                    <button class="cart-add-btn" data-id="${item.id}" data-name="${item.name}" data-price="${item.price}" data-image="${correctedImageUrl}" data-description="${item.description || ''}" style="background:#8b5e3b;color:white;border:none;border-radius:20px;padding:8px 16px;font-size:12px;font-weight:600;cursor:pointer;transition:all 0.3s ease;">
                                        <i class="fas fa-plus"></i> Add to Cart
                                    </button>
                                    <button class="order-food-btn" data-id="${item.id}" data-name="${item.name}" data-price="${item.price}" data-image="${correctedImageUrl}">Order Now</button>
                                </div>
                                <div style="margin-top:12px;text-align:center;flex:1;display:flex;flex-direction:column;justify-content:space-between;width:100%;">
                                    <div style="margin-bottom:8px;">
                                        <strong style="font-size:16px;color:#4e342e;display:block;margin-bottom:4px;">${item.name}</strong>
                                        <span style="font-size:18px;font-weight:600;color:#8b5e3b;">₱${item.price}</span>
                                    </div>
                                    <span style="color:#666;font-size:14px;line-height:1.4;">${item.description || ''}</span>
                                </div>
                            </div>`;
                        });
                        html += '</div>';
                    } else {
                        html = '<div class="text-muted">No menu available.</div>';
                    }
                    foodMenuContent.innerHTML = `<div class='food-menu-content-card'>${html}</div>`;
                    
                    // The cart count badge is already created with the correct count in the HTML above
                    // No need to call updateCartCountBadge() here as it might override the correct value
                    console.log('✅ Food menu modal loaded with cart count badge:', cart.length);
                    
                    // Fallback: Update cart count badge after a short delay to ensure it's visible
                    setTimeout(() => {
                        const cartItemCount = document.getElementById('cartItemCount');
                        if (cartItemCount) {
                            const actualCartCount = cart.length;
                            cartItemCount.textContent = actualCartCount;
                            cartItemCount.style.display = actualCartCount > 0 ? 'flex' : 'none';
                            console.log('✅ Fallback: Updated cart count badge to:', actualCartCount);
                        }
                    }, 50);
                })
                .catch(err => {
                    foodMenuContent.innerHTML = `<div class='food-menu-content-card'><div class='alert alert-danger'>Failed to load menu: ${err}</div></div>`;
                });
        }
    });
    // Remove lingering modal-backdrop and modal-open class when food menu modal is closed
    foodMenuModalEl.addEventListener('hidden.bs.modal', function () {
        // Clear the backdrop check interval
        if (this._backdropCheckInterval) {
            clearInterval(this._backdropCheckInterval);
            this._backdropCheckInterval = null;
        }
        
        document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
        document.body.classList.remove('modal-open');
        document.body.style.removeProperty('padding-right');
        document.body.style.removeProperty('overflow');
        document.body.style = '';
        
        // Ensure the floating button is clickable after modal closes
        const orderFoodBtn = document.getElementById('orderFoodBtn');
        if (orderFoodBtn) {
            orderFoodBtn.style.pointerEvents = 'auto';
            orderFoodBtn.style.opacity = '1';
        }
        
        // Reset modal content
        const foodMenuContent = document.getElementById('food-menu-content');
        if (foodMenuContent) {
            foodMenuContent.innerHTML = '<div class="text-center text-muted"><i class="fas fa-spinner fa-spin me-2"></i>Loading menu...</div>';
        }
    });
}

// Add fade-in animation to food menu modal
if (foodMenuModalEl) {
    foodMenuModalEl.classList.add('fade');
    
    // Ensure smooth show animation
    foodMenuModalEl.addEventListener('show.bs.modal', function () {
        // Force reflow to ensure animation works
        this.offsetHeight;
        this.classList.add('show');
        
        // Ensure the floating button is hidden when modal opens
        const orderFoodBtn = document.getElementById('orderFoodBtn');
        if (orderFoodBtn) {
            orderFoodBtn.style.pointerEvents = 'none';
            orderFoodBtn.style.opacity = '0.5';
        }
    });
    
    // Ensure smooth hide animation
    foodMenuModalEl.addEventListener('hide.bs.modal', function () {
        this.classList.remove('show');
        
        // Ensure the floating button is clickable when modal closes
        const orderFoodBtn = document.getElementById('orderFoodBtn');
        if (orderFoodBtn) {
            orderFoodBtn.style.pointerEvents = 'auto';
            orderFoodBtn.style.opacity = '1';
        }
    });
}

// Floating action button for Order Food
const fabBtn = document.getElementById('view-food-menu-btn-fab');
if (fabBtn) {
    fabBtn.addEventListener('click', function(e) {
        e.preventDefault();
        if (typeof bootstrap !== 'undefined') {
            const foodMenuModal = new bootstrap.Modal(document.getElementById('foodMenuModal'));
            foodMenuModal.show();
        }
    });
}

// Make the floating action button draggable and only open modal on true, quick click (not after drag or long press)
(function() {
    const fab = document.getElementById('view-food-menu-btn-fab');
    if (!fab) return;

    let startX, startY, mouseDownTime = 0, dragMoved = false, blockClick = false;

    fab.addEventListener('mousedown', function(e) {
        mouseDownTime = Date.now();
        startX = e.clientX;
        startY = e.clientY;
        dragMoved = false;
        blockClick = false;
        fab._dragStartLeft = fab.offsetLeft;
        fab._dragStartTop = fab.offsetTop;
        fab.style.transition = 'none';
        document.body.style.userSelect = 'none';
    });

    document.addEventListener('mousemove', function(e) {
        if (mouseDownTime === 0) return;
        const dx = e.clientX - startX;
        const dy = e.clientY - startY;
        if (Math.abs(dx) > 5 || Math.abs(dy) > 5) { // Use a slightly larger threshold
            dragMoved = true;
            blockClick = true;
            let newLeft = fab._dragStartLeft + dx;
            let newTop = fab._dragStartTop + dy;
            // Clamp within viewport
            const minTop = 80;
            const maxTop = window.innerHeight - fab.offsetHeight - 16;
            const minLeft = 0;
            const maxLeft = window.innerWidth - fab.offsetWidth - 16;
            newTop = Math.max(minTop, Math.min(newTop, maxTop));
            newLeft = Math.max(minLeft, Math.min(newLeft, maxLeft));
            fab.style.position = 'fixed';
            fab.style.left = newLeft + 'px';
            fab.style.top = newTop + 'px';
            fab.style.right = 'auto';
            fab.style.bottom = 'auto';
        }
    });

    document.addEventListener('mouseup', function() {
        mouseDownTime = 0;
        fab.style.transition = '';
        document.body.style.userSelect = '';
    });

    fab.addEventListener('click', function(e) {
        if (blockClick) {
            e.preventDefault();
            blockClick = false;
            dragMoved = false;
            return;
        }
        // Only open modal if not dragged and quick click
        if (!dragMoved) {
            if (typeof bootstrap !== 'undefined') {
                const foodMenuModal = new bootstrap.Modal(document.getElementById('foodMenuModal'));
                foodMenuModal.show();
            }
        }
        e.preventDefault();
        mouseDownTime = 0;
        dragMoved = false;
    });

    // Touch support
    let touchStartX, touchStartY, touchMoved = false;
    fab.addEventListener('touchstart', function(e) {
        if (e.touches.length !== 1) return;
        touchMoved = false;
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
        fab._dragStartLeft = fab.offsetLeft;
        fab._dragStartTop = fab.offsetTop;
        fab.style.transition = 'none';
    }, { passive: false });

    fab.addEventListener('touchmove', function(e) {
        if (e.touches.length !== 1) return;
        const dx = e.touches[0].clientX - touchStartX;
        const dy = e.touches[0].clientY - touchStartY;
        if (Math.abs(dx) > 5 || Math.abs(dy) > 5) {
            touchMoved = true;
            let newLeft = fab._dragStartLeft + dx;
            let newTop = fab._dragStartTop + dy;
            // Clamp within viewport
            const minTop = 80;
            const maxTop = window.innerHeight - fab.offsetHeight - 16;
            const minLeft = 0;
            const maxLeft = window.innerWidth - fab.offsetWidth - 16;
            newTop = Math.max(minTop, Math.min(newTop, maxTop));
            newLeft = Math.max(minLeft, Math.min(newLeft, maxLeft));
            fab.style.position = 'fixed';
            fab.style.left = newLeft + 'px';
            fab.style.top = newTop + 'px';
            fab.style.right = 'auto';
            fab.style.bottom = 'auto';
        }
    }, { passive: false });

    fab.addEventListener('touchend', function(e) {
        fab.style.transition = '';
        if (!touchMoved) {
            if (typeof bootstrap !== 'undefined') {
                const foodMenuModal = new bootstrap.Modal(document.getElementById('foodMenuModal'));
                foodMenuModal.show();
            }
        }
    });
})();

// Dynamic price calculation
function calculatePrice() {
    const checkIn = new Date(document.getElementById('check_in').value);
    const checkOut = new Date(document.getElementById('check_out').value);
    const pricePerNight = parseFloat(document.getElementById('price_per_night').value);
    
    if (checkIn && checkOut && pricePerNight) {
        const nights = Math.ceil((checkOut - checkIn) / (1000 * 60 * 60 * 24));
        const totalPrice = nights * pricePerNight;
        document.getElementById('total_price').textContent = totalPrice.toFixed(2);
    }
}

// Star rating system
function setRating(rating) {
    document.getElementById('rating').value = rating;
    const stars = document.querySelectorAll('.rating-star');
    stars.forEach((star, index) => {
        star.classList.toggle('active', index < rating);
    });
}

// Amenity selection
function toggleAmenity(amenityId) {
    const checkbox = document.getElementById(`amenity-${amenityId}`);
    const card = checkbox.closest('.amenity-card');
    card.classList.toggle('selected');
}

// Search and filter rooms
function filterRooms() {
    const searchTerm = document.getElementById('search').value.toLowerCase();
    const rooms = document.querySelectorAll('.room-card');
    
    rooms.forEach(room => {
        const roomType = room.querySelector('.room-type').textContent.toLowerCase();
        const roomNumber = room.querySelector('.room-number').textContent.toLowerCase();
        
        if (roomType.includes(searchTerm) || roomNumber.includes(searchTerm)) {
            room.style.display = 'block';
        } else {
            room.style.display = 'none';
        }
    });
}

// Confirmation dialogs
function confirmDelete(itemType, itemId) {
    return confirm(`Are you sure you want to delete this ${itemType}?`);
}

function confirmCancel(bookingId) {
    return confirm('Are you sure you want to cancel this booking?');
}

// Toast notifications
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type} show`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Image preview
function previewImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('image-preview').src = e.target.result;
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Responsive table
function makeTableResponsive() {
    const tables = document.querySelectorAll('.table-responsive table');
    tables.forEach(table => {
        const headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent);
        const cells = table.querySelectorAll('td');
        
        cells.forEach((cell, index) => {
            cell.setAttribute('data-label', headers[index % headers.length]);
        });
    });
}

// Initialize all responsive tables
document.addEventListener('DOMContentLoaded', makeTableResponsive);

// Profile dropdown functionality
function toggleProfileDropdown(event) {
    event.preventDefault();
    const dropdown = document.getElementById('profileDropdown');
    dropdown.classList.toggle('show');
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const dropdown = document.getElementById('profileDropdown');
    const profileLink = document.querySelector('.profile-section a');
    
    if (!profileLink.contains(event.target) && !dropdown.contains(event.target)) {
        dropdown.classList.remove('show');
        document.body.style.overflow = '';
    }
}); 

document.addEventListener('DOMContentLoaded', function() {
  var toggler = document.getElementById('navbar-toggler');
  var menu = document.getElementById('navbar-menu');
  if (toggler && menu) {
    toggler.addEventListener('click', function(e) {
      e.stopPropagation();
      menu.classList.toggle('active');
    });
  }
  document.addEventListener('click', function(e) {
    if (menu && menu.classList.contains('active')) {
      if (!menu.contains(e.target) && e.target !== toggler) {
        menu.classList.remove('active');
      }
    }
  });
});

// Add these at the top of the file or before the click handler:
let selectedItemName = '';
let selectedItemPrice = '';
let selectedItemImage = '';
let selectedItemDescription = '';

// In the order-food-btn click handler, set these values:
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('order-food-btn')) {
        // Get user info from hidden fields with fallback values
        const userId = document.getElementById('user-id')?.value || '';
        const userName = document.getElementById('user-name')?.value || 'Guest User';
        const userPhone = document.getElementById('user-phone')?.value || '+639000000000';
        const userAddress = document.getElementById('user-address')?.value || 'Santa Cruz, Laguna';
        const userEmail = document.getElementById('user-email')?.value || 'guest@example.com'; // Get user email
        
        // Log user info for debugging (remove in production)
        console.log('User Info Retrieved:', { userId, userName, userPhone, userEmail });
        
        // Validate user information and show warning if incomplete
        if (!userName || userName === 'Guest User' || !userEmail || userEmail === 'guest@example.com') {
            console.warn('User information may be incomplete. Please ensure user is logged in.');
        }

        // Get item info
        const itemId = e.target.getAttribute('data-id');
        const itemName = e.target.getAttribute('data-name');
        const itemPrice = e.target.getAttribute('data-price');
        const itemImage = e.target.getAttribute('data-image');
        // Extract description from the DOM (adjust selector as needed)
        const itemDescription = e.target.closest('.food-menu-item').querySelector('span')?.textContent.trim() || '';
        selectedItemName = itemName;
        selectedItemPrice = itemPrice;
        selectedItemImage = itemImage;
        selectedItemDescription = itemDescription;

        // Get approved bookings from a global JS variable or hidden JSON
        let approvedBookings = [];
        const approvedBookingsInput = document.getElementById('approved-bookings-json');
        if (approvedBookingsInput) {
            try {
                approvedBookings = JSON.parse(approvedBookingsInput.value);
            } catch (e) { approvedBookings = []; }
        } else {
            approvedBookings = [];
        }

// If no approved bookings available, fetch them
if (approvedBookings.length === 0) {
    fetchApprovedBookings();
}

        // Barangay and sitio data (hardcoded for now)
        const barangays = [
            'Alipit','Bagumbayan','Bubukal','Calios','Duhat','Gatid','Labuin','Malinao','Oogong','Pagsawitan','Palasan','Patimbao','Poblacion I','Poblacion II','Poblacion III','Poblacion IV','San Jose','San Juan','San Pablo Norte','San Pablo Sur','Santa Cruz Putol','Santo Angel Central','Santo Angel Norte','Santo Angel Sur','Santisima Cruz','Sapa','Tagapo'
        ];
        const sitiosByBarangay = {
            'Alipit': ['Sitio Uno','Sitio Dos','Sitio Tres'],
            'Bagumbayan': ['Purok 1','Purok 2','Purok 3'],
            'Bubukal': ['Spring Side','Central','Riverside'],
            'Calios': ['Lakeview','Market Area','Fishermen\'s Village'],
            'Duhat': ['Orchard Side','Main Road','Interior'],
            'Gatid': ['Rice Field Area','Highway Side','School Zone'],
            'Labuin': ['Farmers Village','Centro','Riverside'],
            'Malinao': ['Lakeside','Upper Malinao','Lower Malinao'],
            'Oogong': ['Main','Riverside','Market Area'],
            'Pagsawitan': ['Centro','Riverside','Highway'],
            'Palasan': ['Upper Palasan','Lower Palasan','Central'],
            'Patimbao': ['Main Road','Interior','Riverside'],
            'Poblacion I': ['Plaza Area','Market Side','Church Area'],
            'Poblacion II': ['Commercial District','School Zone','Residential Area'],
            'Poblacion III': ['Main Street','Park Side','Market Area'],
            'Poblacion IV': ['Town Center','Business District','Residential Zone'],
            'San Jose': ['Upper San Jose','Lower San Jose','Central'],
            'San Juan': ['Riverside','Centro','Highway'],
            'San Pablo Norte': ['Upper Area','Central','Highway Side'],
            'San Pablo Sur': ['Main Road','Interior','Market Area'],
            'Santa Cruz Putol': ['Central','Riverside','Highway'],
            'Santo Angel Central': ['Plaza Area','Church Side','Market Zone'],
            'Santo Angel Norte': ['Upper Area','Central','Lower Area'],
            'Santo Angel Sur': ['Main Road','Interior','Highway Side'],
            'Santisima Cruz': ['Church Area','Plaza Side','Residential Zone'],
            'Sapa': ['Riverside','Central','Market Area'],
            'Tagapo': ['Upper Tagapo','Lower Tagapo','Central']
        };

        // Build dropdown HTML
        let dropdownHtml = '';
        if (approvedBookings.length > 0) {
            dropdownHtml = `<div style='margin-bottom:16px;text-align:left;'>
                <label for='deliveryBookingSelect' style='font-weight:600;'>Select Room for Delivery:</label>
                <select id='deliveryBookingSelect' class='form-select' style='max-width:340px;'>
                    <option value='' disabled selected>Select a room</option>`;
            approvedBookings.forEach(b => {
                dropdownHtml += `<option value='${b.id}'>Room ${b.room_number} (${b.room_type}) - Booking #${b.id}</option>`;
            });
            dropdownHtml += `</select></div>`;
        } else {
            dropdownHtml = `<div class='text-danger mb-3' style='text-align:left;'>No approved rooms available for delivery.</div>`;
        }

        // Build order summary HTML as a form
        const summaryHtml = `
            <form id="orderDeliveryForm" autocomplete="off" style="max-width:1200px;width:100%;margin:0;padding:12px 32px;border-radius:24px;background:#f8f9fa;box-shadow:0 4px 24px rgba(0,0,0,0.08);font-size:1.15rem;">
                <div style="display:flex;align-items:center;margin-bottom:18px;">
  <button type="button" id="backFromDeliveryDetailsBtn" style="background:none;border:none;font-size:1.8rem;color:#6D4C41;margin-right:12px;cursor:pointer;line-height:1;" aria-label="Back">&#8592;</button>
  <h3 style='font-weight:700;margin:0;'>Delivery Details</h3>
</div>

                <!-- Room Selection Section -->
                <div class="mb-4" style="background:#fff;padding:16px;border-radius:12px;border:2px solid #6D4C41;">
                    <h5 style='margin-top:0;margin-bottom:12px;color:#6D4C41;'>Room Selection <span style="color:red">*</span></h5>
                    <div class="mb-2">
                        <label for="approvedRoomSelect" class="form-label">Select Room for Delivery</label>
                        <select id="approvedRoomSelect" class="form-select" required>
                            <option value="" disabled selected>Select a room</option>
                            ${approvedBookings.map(b => `<option value="${b.id}">Room ${b.room_number} (${b.room_type}) - Booking #${b.id}</option>`).join('')}
                        </select>
                        <div class="invalid-feedback">Please select a room for delivery.</div>
                    </div>
                    <div class="mb-2">
                        <label for="orderDeliveryNotes" class="form-label">Delivery Notes</label>
                        <textarea id="orderDeliveryNotes" class="form-control" placeholder="Room info will appear here" aria-label="Delivery Notes" readonly></textarea>
                    </div>
                </div>

                <!-- Payment Method Section -->
                <div class="mb-4" style="background:#fff;padding:16px;border-radius:12px;border:2px solid #6D4C41;">
                    <h5 style='margin-top:0;margin-bottom:12px;color:#6D4C41;'>Payment Method <span style="color:red">*</span></h5>
                    <div class="mb-2">
                        <select id="paymentMethodSelect" class="form-select" required aria-label="Payment Method">
                            <option value="" disabled selected>Select payment method</option>
                            <option value="cod">Cash on Delivery</option>
                            <option value="gcash">GCash</option>
                            <option value="half_payment">Half Payment (GCash + COD)</option>
                        </select>
                        <div class="invalid-feedback">Please select a payment method.</div>
                    </div>
                    <div id="gcashQrSection" style="display:none;text-align:left;margin-top:12px;">
                        <button type="button" id="showGcashQrBtn" class="btn" style="background:rgba(109,76,65,0.08);color:#6D4C41;font-weight:600;border-radius:2rem;padding:0.55em 2.2em;display:inline-flex;align-items:center;gap:0.9em;border:2px solid #6D4C41;">
                            <i class="fas fa-qrcode" aria-hidden="true" style="font-size:1.2em;"></i> Show Electronic Payment
                        </button>
                    </div>
                </div>

                <h5 style='margin-top:24px;margin-bottom:10px;'>Contact Information <span style="font-size:0.9em;color:#6c757d;font-weight:normal;">(Auto-filled from your profile)</span></h5>
                <div class="mb-2">
                    <label for="orderFullName" class="form-label">Full Name</label>
                    <div class="input-group">
                        <input type="text" id="orderFullName" class="form-control" value="${userName}" readonly aria-label="Full Name" style="background-color:#f8f9fa;border-color:#dee2e6;">
                        <span class="input-group-text" style="background-color:#e7d7ce;border-color:#dee2e6;color:#6D4C41;">
                            <i class="fas fa-user-check"></i>
                        </span>
                    </div>
                </div>
                <div class="mb-2">
                    <label for="orderEmail" class="form-label">Email</label>
                    <div class="input-group">
                        <input type="email" id="orderEmail" class="form-control" value="${userEmail}" placeholder="your@email.com" autocomplete="email" required aria-label="Email" readonly style="background-color:#f8f9fa;border-color:#dee2e6;">
                        <span class="input-group-text" style="background-color:#e7d7ce;border-color:#dee2e6;color:#6D4C41;">
                            <i class="fas fa-envelope"></i>
                        </span>
                    </div>
                    <div class="invalid-feedback" id="orderEmailError" style="display:none;">Please enter a valid email address.</div>
                </div>
                <div class="mb-2">
                    <label for="orderPhone" class="form-label">Phone Number</label>
                    <div class="input-group">
                        <input type="tel" id="orderPhone" class="form-control" value="${userPhone}" readonly style="background-color:#f8f9fa;border-color:#dee2e6;">
                        <span class="input-group-text" style="background-color:#e7d7ce;border-color:#dee2e6;color:#6D4C41;">
                            <i class="fas fa-phone"></i>
                        </span>
                    </div>
                    <div class="invalid-feedback" id="orderPhoneError" style="display:none;">Please enter a valid phone number.</div>
                </div>

                <h5 style='margin-top:24px;margin-bottom:10px;'>Delivery Address</h5>
                <div class="mb-2">
                    <label for="orderBarangay" class="form-label">Barangay</label>
                    <select id="orderBarangay" class="form-select" required aria-label="Barangay" readonly>
                        <option value="Santa Cruz" selected>Santa Cruz</option>
                    </select>
                </div>
                <div class="mb-2">
                    <label for="orderSitio" class="form-label">Sitio/Purok</label>
                    <select id="orderSitio" class="form-select" required aria-label="Sitio/Purok" readonly>
                        <option value="Central" selected>Central</option>
                    </select>
                </div>
                <div class="mb-2">
                    <label for="orderLandmarks" class="form-label">Landmarks</label>
                    <input type="text" id="orderLandmarks" class="form-control" placeholder="Nearby landmarks or additional directions" aria-label="Landmarks" value="Fawna Hotel" readonly>
                </div>

                <!-- Order Summary -->
                <div class="mb-4" style="background:#fff;padding:16px;border-radius:12px;margin-top:24px;">
                    <h5 style='margin-top:0;margin-bottom:12px;'>Order Summary</h5>
                    <div id="orderedFoodDisplay" style="border:1px solid #e0e0e0;border-radius:8px;padding:12px 16px;margin-bottom:16px;display:flex;align-items:center;gap:16px;">
                  <img src="${selectedItemImage}" alt="${selectedItemName}" style="width:60px;height:60px;object-fit:cover;border-radius:8px;">
                  <div>
                    <div style="font-weight:600;font-size:1.1rem;">${selectedItemName}</div>
                    <div style="color:#555;font-size:0.98rem;margin-bottom:2px;">${selectedItemDescription || ''}</div>
                    <div style="color:#6D4C41;font-weight:500;">₱${selectedItemPrice}</div>
                  </div>
                </div>
                    <div id="orderBreakdown" style="font-size:1.08em;color:#4e342e;">
                        <div style="display:flex;justify-content:space-between;"><span>Subtotal:</span><span>₱${selectedItemPrice}</span></div>
                        <div style="display:flex;justify-content:space-between;"><span>Delivery Fee:</span><span>₱50.00</span></div>
                        <div style="display:flex;justify-content:space-between;font-weight:700;border-top:1px solid #e0e0e0;margin-top:8px;padding-top:8px;"><span>Total:</span><span>₱${(parseFloat(selectedItemPrice) + 50).toFixed(2)}</span></div>
                </div>
                </div>

                <div class="mt-4" style="text-align:center;">
                    <button type="submit" class="btn btn-lg btn-primary" id="confirmOrderBtn" style="min-width:160px;margin-right:12px;background:#8b5e3b;border:none;">
                        <span id="confirmOrderBtnText">Confirm Order</span>
                        <span id="confirmOrderSpinner" class="spinner-border spinner-border-sm" style="display:none;" role="status" aria-hidden="true"></span>
                    </button>
                    <button type="button" class="btn btn-lg btn-secondary" id="cancelOrderBtn" style="min-width:120px;">Cancel</button>
                </div>
            </form>`;

        // Replace the menu content with the summary
        const menuContent = document.getElementById('food-menu-content');
        if (menuContent) {
            menuContent.innerHTML = `<div class='food-menu-content-card'>${summaryHtml}</div>`;
            setTimeout(() => {
              const backBtn = document.getElementById('backFromDeliveryDetailsBtn');
              if (backBtn) {
                backBtn.onclick = function() {
                  // Redirect to the food menu view
                  if (typeof showFoodMenuModal === 'function') {
                    showFoodMenuModal();
                  }
                };
              }
            }, 100);
        }

        // Populate sitio options when barangay changes
        setTimeout(() => {
            const barangaySelect = document.getElementById('orderBarangay');
            const sitioSelect = document.getElementById('orderSitio');
            if (barangaySelect && sitioSelect) {
                barangaySelect.addEventListener('change', function() {
                    const val = this.value;
                    sitioSelect.innerHTML = '<option value="">Select Sitio/Purok</option>';
                    if (val && sitiosByBarangay[val]) {
                        sitiosByBarangay[val].forEach(sitio => {
                            const opt = document.createElement('option');
                            opt.value = sitio;
                            opt.textContent = sitio;
                            sitioSelect.appendChild(opt);
                        });
                        sitioSelect.disabled = false;
                    } else {
                        sitioSelect.disabled = true;
                    }
                });
            }

            // Handle confirm/cancel
            const form = document.getElementById('orderDeliveryForm');
            if (form) {
                form.onsubmit = function(e) {
                    e.preventDefault();
                    
                    // Validate all required fields
                    const roomSelect = document.getElementById('approvedRoomSelect');
                    const paymentSelect = document.getElementById('paymentMethodSelect');
                    const emailInput = document.getElementById('orderEmail');
                    const phoneInput = document.getElementById('orderPhone');
                    
                    let valid = true;

                    // Room selection validation
                    if (!roomSelect.value) {
                        roomSelect.classList.add('is-invalid');
                        valid = false;
                    } else {
                        roomSelect.classList.remove('is-invalid');
                    }

                    // Payment method validation
                    if (!paymentSelect.value) {
                        paymentSelect.classList.add('is-invalid');
                        valid = false;
                    } else {
                        paymentSelect.classList.remove('is-invalid');
                    }

                    // Email validation
                    if (!emailInput.value || !/^\S+@\S+\.\S+$/.test(emailInput.value)) {
                        emailInput.classList.add('is-invalid');
                        document.getElementById('orderEmailError').style.display = '';
                        valid = false;
                    } else {
                        emailInput.classList.remove('is-invalid');
                        document.getElementById('orderEmailError').style.display = 'none';
                    }

                    // Phone validation
                    if (!phoneInput.value) {
                        phoneInput.classList.add('is-invalid');
                        document.getElementById('orderPhoneError').style.display = '';
                        valid = false;
                    } else {
                        phoneInput.classList.remove('is-invalid');
                        document.getElementById('orderPhoneError').style.display = 'none';
                    }

                    if (!valid) {
                        // Show error message at the top of the form
                        const errorDiv = document.createElement('div');
                        errorDiv.className = 'alert alert-danger';
                        errorDiv.style.marginBottom = '20px';
                        errorDiv.innerHTML = 'Please fill in all required fields marked with <span style="color:red">*</span>';
                        form.insertBefore(errorDiv, form.firstChild);
                        
                        // Remove error message after 3 seconds
                        setTimeout(() => {
                            errorDiv.remove();
                        }, 3000);
                        
                        return;
                    }

                    // Compose delivery address
                    const barangay = document.getElementById('orderBarangay').value.trim();
                    const sitio = document.getElementById('orderSitio').value.trim();
                    const landmarks = document.getElementById('orderLandmarks').value.trim();
                    let deliveryAddress = '';
                    if (sitio) deliveryAddress += sitio;
                    if (barangay) deliveryAddress += ', ' + barangay;
                    deliveryAddress += ', Santa Cruz, Laguna';
                    if (landmarks) deliveryAddress += ' (' + landmarks + ')';
                    const deliveryNotesField = document.getElementById('orderDeliveryNotes');
                    let deliveryNotesValue = deliveryNotesField ? deliveryNotesField.value : '';
                    const orderedItemLine = `Ordered Item: ${selectedItemName} (₱${selectedItemPrice})`;
                    if (!deliveryNotesValue.startsWith(orderedItemLine)) {
                        deliveryNotesValue = `${orderedItemLine}\n` + deliveryNotesValue;
                    }
                    const payload = {
                        user_id: userId,
                        full_name: document.getElementById('orderFullName').value,
                        email: document.getElementById('orderEmail').value,
                        phone: document.getElementById('orderPhone').value,
                        delivery_address: deliveryAddress,
                        payment_method: document.getElementById('paymentMethodSelect').value,
                        notes: '',
                        delivery_notes: deliveryNotesValue,
                        subtotal: selectedItemPrice,
                        delivery_fee: 50,
                        total_amount: parseFloat(selectedItemPrice) + 50,
                        menu_item_id: itemId,  // Add the menu_item_id directly to the order
                        items: [
                            {
                                menu_item_id: itemId,
                                quantity: 1,
                                price: selectedItemPrice
                            }
                        ]
                    };
                    // Disable button and show spinner
                    const confirmOrderBtn = document.getElementById('confirmOrderBtn');
                    const confirmOrderBtnText = document.getElementById('confirmOrderBtnText');
                    const confirmOrderSpinner = document.getElementById('confirmOrderSpinner');
                    confirmOrderBtn.disabled = true;
                    confirmOrderBtnText.textContent = 'Processing...';
                    confirmOrderSpinner.style.display = '';
                    fetch('/api/order-food', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
                        },
                        body: JSON.stringify(payload)
                    })
                    .then(res => res.json())
                    .then(data => {
                        confirmOrderBtn.disabled = false;
                        confirmOrderBtnText.textContent = 'Confirm Order';
                        confirmOrderSpinner.style.display = 'none';
                        if (data.success) {
                            // Hide Delivery Details modal if present
                            const deliveryDetailsModal = document.getElementById('deliveryDetailsModal');
                            if (deliveryDetailsModal && typeof bootstrap !== 'undefined') {
                                const ddModalInstance = bootstrap.Modal.getInstance(deliveryDetailsModal);
                                if (ddModalInstance) ddModalInstance.hide();
                            }
                            // Hide Food Menu modal if present
                            const foodMenuModal = document.getElementById('foodMenuModal');
                            if (foodMenuModal && typeof bootstrap !== 'undefined') {
                                const fmModalInstance = bootstrap.Modal.getInstance(foodMenuModal);
                                if (fmModalInstance) fmModalInstance.hide();
                            }
                            
                            // Show proper success message
                            showOrderSuccessMessage('Order placed successfully! Your food will be delivered to your room shortly.');
                            
                            // Show the order success modal
                            const orderSuccessModal = new bootstrap.Modal(document.getElementById('orderSuccessModal'), {
                                backdrop: 'static',
                                keyboard: false
                            });
                            orderSuccessModal.show();
                        } else {
                            showOrderErrorMessage(data.message || 'Failed to place order. Please try again.');
                        }
                    })
                    .catch(err => {
                        confirmOrderBtn.disabled = false;
                        confirmOrderBtnText.textContent = 'Confirm Order';
                        confirmOrderSpinner.style.display = 'none';
                        showOrderErrorMessage('Order failed. Please try again.');
                    });
                };
            }
            const cancelBtn = document.getElementById('cancelOrderBtn');
            if (cancelBtn) {
                cancelBtn.onclick = function() {
                    location.reload();
                };
            }

            // Set up approved room dropdown to update delivery notes
            const approvedRoomSelect = document.getElementById('approvedRoomSelect');
            const deliveryNotes = document.getElementById('orderDeliveryNotes');
            function updateDeliveryNotesFromDropdown() {
                console.log('approvedBookings:', approvedBookings);
                const roomSelectValue = approvedRoomSelect.value;
                console.log('approvedRoomSelect.value:', roomSelectValue);
                // Try both string and number comparison
                const selected = approvedBookings.find(b => b.id == roomSelectValue || b.id === roomSelectValue);
                console.log('selected booking:', selected);
                let notes = '';
                let roomInfoDiv = document.getElementById('selectedRoomInfo');
                if (!roomInfoDiv) {
                    // Insert after orderedFoodDisplay
                    const foodDisplay = document.getElementById('orderedFoodDisplay');
                    roomInfoDiv = document.createElement('div');
                    roomInfoDiv.id = 'selectedRoomInfo';
                    roomInfoDiv.style = 'margin: 8px 0 0 0; font-size: 1.05em; color: #4e342e; font-weight: 500;';
                    if (foodDisplay && foodDisplay.parentNode) {
                        foodDisplay.parentNode.insertBefore(roomInfoDiv, foodDisplay.nextSibling);
                    }
                }
                if (selected) {
                    notes = `Room ${selected.room_number} (${selected.room_type}) - Booking #${selected.id}`;
                    roomInfoDiv.textContent = `Room: ${selected.room_number} (${selected.room_type}) | Booking #${selected.id}`;
                    roomInfoDiv.style.display = '';
                    console.log('Room info div updated:', roomInfoDiv.textContent);
                } else {
                    roomInfoDiv.textContent = '';
                    roomInfoDiv.style.display = 'none';
                    console.log('Room info div hidden');
                }
                // Fix: define orderedItemLine here
                const orderedItemLine = `Ordered Item: ${selectedItemName} (₱${selectedItemPrice})`;
                if (selectedItemName && selectedItemPrice) {
                    notes = `${orderedItemLine}\n` + notes;
                }
                deliveryNotes.value = notes;
            }
            if (approvedRoomSelect && deliveryNotes) {
                approvedRoomSelect.addEventListener('change', updateDeliveryNotesFromDropdown);
            }
            // Always update delivery notes after rendering the form
            if (deliveryNotes) {
                    updateDeliveryNotesFromDropdown();
            }

            // Payment method QR logic
            const paymentSelect = document.getElementById('paymentMethodSelect');
            const gcashQrSection = document.getElementById('gcashQrSection');
            const showGcashQrBtn = document.getElementById('showGcashQrBtn');
            if (paymentSelect && gcashQrSection) {
                paymentSelect.addEventListener('change', function() {
                    if (this.value === 'gcash' || this.value === 'half_payment') {
                        gcashQrSection.style.display = '';
                    } else {
                        gcashQrSection.style.display = 'none';
                    }
                });
            }
            if (showGcashQrBtn) {
                showGcashQrBtn.onclick = function(e) {
                    e.preventDefault();
                    // Move the modal to body if not already there
                    const modalEl = document.getElementById('gcashQrModal');
                    if (modalEl && modalEl.parentNode !== document.body) {
                        document.body.appendChild(modalEl);
                    }
                    // Open with static backdrop
                    const modal = new bootstrap.Modal(modalEl, { backdrop: 'static', keyboard: true, focus: true });
                    modal.show();
                };
            }
        }, 100);
    }
}); 
/* Animation for food menu grid */
const style = document.createElement('style');
style.innerHTML = `
.food-menu-grid.fade {
  opacity: 0;
  transition: opacity 0.3s;
}
.food-menu-grid.fade.show {
  opacity: 1;
  transition: opacity 0.3s;
}`;
document.head.appendChild(style); 

document.addEventListener('click', function(e) {
    if (e.target.classList.contains('food-cat-btn')) {
        const cat = e.target.getAttribute('data-cat');
        // Skip if it's the Your Orders button (handled separately)
        if (e.target.id === 'yourOrdersCatBtn') return;
        
        // Remove active from all, add to clicked
        document.querySelectorAll('.food-cat-btn').forEach(btn => btn.classList.remove('active'));
        e.target.classList.add('active');
        
        // Ensure modal backdrop is visible when switching food categories
        const modal = document.getElementById('foodMenuModal');
        if (modal && typeof bootstrap !== 'undefined') {
            const modalInstance = bootstrap.Modal.getInstance(modal);
            if (modalInstance) {
                // Force backdrop to be visible
                const backdrop = document.querySelector('.modal-backdrop');
                if (!backdrop) {
                    const newBackdrop = document.createElement('div');
                    newBackdrop.className = 'modal-backdrop fade show';
                    document.body.appendChild(newBackdrop);
                }
                // Ensure body has modal-open class
                document.body.classList.add('modal-open');
            }
        }
        
        const grid = document.querySelector('.food-menu-grid');
        if (grid) {
            grid.classList.remove('show');
            grid.classList.add('fade');
            setTimeout(() => {
                document.querySelectorAll('.food-menu-item').forEach(item => {
                    if (cat === 'All' || item.getAttribute('data-category') === cat) {
                        item.style.display = '';
                    } else {
                        item.style.display = 'none';
                    }
                });
                grid.classList.add('show');
            }, 200);
            setTimeout(() => {
                grid.classList.remove('fade');
            }, 500);
        } else {
            document.querySelectorAll('.food-menu-item').forEach(item => {
                if (cat === 'All' || item.getAttribute('data-category') === cat) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        }
    }
}); 

// Function to handle Your Orders button click
function handleYourOrdersClick(e) {
    if (e.target && e.target.id === 'yourOrdersCatBtn') {
        console.log('Your Orders button clicked!');
        console.log('Button element:', e.target);
        console.log('Button text:', e.target.textContent);
        
        // Check for duplicate IDs (this could cause issues)
        const allYourOrdersBtns = document.querySelectorAll('#yourOrdersCatBtn');
        if (allYourOrdersBtns.length > 1) {
            console.warn('WARNING: Multiple elements with ID "yourOrdersCatBtn" found!', allYourOrdersBtns);
        }
        
        // Remove 'active' from all category buttons and cart button
        document.querySelectorAll('.food-cat-btn').forEach(btn => {
            btn.classList.remove('active');
            console.log('Removed active from:', btn.textContent || btn.id);
        });
        
        // Set 'active' on this button specifically
        e.target.classList.add('active');
        console.log('Added active to Your Orders button (handleYourOrdersClick)');
        
        // Load order history
        console.log('Calling loadYourOrders function...');
        loadYourOrders();
    }
}

// Direct event handler for Your Orders button
function handleYourOrdersClickDirect(e) {
    e.preventDefault();
    e.stopPropagation();
    console.log('Your Orders button clicked (direct event handler)!');
    
    // Remove 'active' from all category buttons and cart button
    document.querySelectorAll('.food-cat-btn').forEach(btn => {
        btn.classList.remove('active');
        console.log('Removed active from:', btn.textContent || btn.id);
    });
    
    // Set 'active' on this button specifically
    this.classList.add('active');
    console.log('Added active to Your Orders button');
    
    // Load order history
    loadYourOrders();
}

// Function to ensure all Your Orders buttons have proper event handling
function ensureYourOrdersButtonEvents() {
    const yourOrdersBtns = document.querySelectorAll('#yourOrdersCatBtn');
    console.log(`Found ${yourOrdersBtns.length} Your Orders button(s)`);
    
    yourOrdersBtns.forEach((btn, index) => {
        console.log(`Setting up event listener for Your Orders button ${index + 1}`);
        
        // Remove any existing event listeners to prevent duplicates
        btn.removeEventListener('click', handleYourOrdersClick);
        btn.removeEventListener('click', handleYourOrdersClickDirect);
        
        // Add the event listener directly to the button for immediate response
        btn.addEventListener('click', handleYourOrdersClickDirect);
        
        // Also add onclick handler for extra reliability
        btn.onclick = function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log(`Your Orders button ${index + 1} clicked (onclick handler)!`);
            
            // Remove 'active' from all category buttons and cart button
            document.querySelectorAll('.food-cat-btn').forEach(btn => {
                btn.classList.remove('active');
                console.log('Removed active from:', btn.textContent || btn.id);
            });
            
            // Set 'active' on this button specifically
            this.classList.add('active');
            console.log('Added active to Your Orders button (ensureYourOrdersButtonEvents)');
            
            // Load order history
            loadYourOrders();
        };
    });
}

// Add event listener at document level for Your Orders button
document.addEventListener('click', function(e) {
    // Check if the clicked element is the Your Orders button
    if (e.target && e.target.id === 'yourOrdersCatBtn') {
        console.log('Your Orders button clicked (document-level delegation)!');
        e.preventDefault();
        e.stopPropagation();
        
        // Remove 'active' from all category buttons and cart button
        document.querySelectorAll('.food-cat-btn').forEach(btn => {
            btn.classList.remove('active');
            console.log('Removed active from:', btn.textContent || btn.id);
        });
        
        // Set 'active' on this button specifically
        e.target.classList.add('active');
        console.log('Added active to Your Orders button (document-level)');
        
        // Load order history
        loadYourOrders();
    }
}); 

// Cancellation reason dropdown logic
const cancelReasonSelect = document.getElementById('cancel_reason_select');
const cancelOtherReasonGroup = document.getElementById('cancel_other_reason_group');
const cancelOtherReason = document.getElementById('cancel_other_reason');
if (cancelReasonSelect && cancelOtherReasonGroup) {
    cancelReasonSelect.addEventListener('change', function() {
        if (this.value === 'Other') {
            cancelOtherReasonGroup.style.display = 'block';
            cancelOtherReason.required = true;
        } else {
            cancelOtherReasonGroup.style.display = 'none';
            cancelOtherReason.required = false;
            cancelOtherReason.value = '';
        }
    });
}

// Update cancel booking logic to send both reason and other_reason
const confirmCancelBtn = document.getElementById('confirmCancel');
if (confirmCancelBtn) {
    confirmCancelBtn.addEventListener('click', function() {
        const form = document.getElementById('cancelBookingForm');
        const bookingId = document.getElementById('cancel_booking_id').value;
        const reasonSelect = document.getElementById('cancel_reason_select').value;
        const otherReasonTextarea = document.getElementById('cancel_other_reason').value;
        const modal = bootstrap.Modal.getInstance(document.getElementById('cancelBookingModal'));
        let reason = '';
        if (reasonSelect === 'Other') {
            if (!otherReasonTextarea) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Required',
                    text: 'Please provide a reason for cancellation.',
                    confirmButtonColor: '#6D4C41'
                });
                return;
            }
            reason = otherReasonTextarea;
        } else {
            reason = reasonSelect;
        }
        if (!reason) {
            Swal.fire({
                icon: 'warning',
                title: 'Required',
                text: 'Please select a reason for cancellation.',
                confirmButtonColor: '#6D4C41'
            });
            return;
        }
        // Show loading state
        const confirmButton = document.getElementById('confirmCancel');
        const originalText = confirmButton.innerHTML;
        confirmButton.disabled = true;
        confirmButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        fetch(`/bookings/${bookingId}/cancel`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
            },
            body: JSON.stringify({
                reason: reason,
                reason_select: reasonSelect,
                other_reason: otherReasonTextarea
            }),
            credentials: 'same-origin'
        })
        .then(async response => {
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.message || 'Failed to cancel booking');
            }
            return data;
        })
        .then(data => {
            // Close the modal first
            modal.hide();
            // Show success message
            Swal.fire({
                icon: 'success',
                title: 'Success',
                text: data.message || 'Booking cancelled successfully',
                showConfirmButton: false,
                timer: 2000
            }).then(() => {
                // Reload the page after the message
                window.location.reload();
            });
        })
        .catch(error => {
            console.error('Error:', error);
            // Show error message
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: error.message || 'An error occurred while cancelling the booking. Please try again.',
                confirmButtonColor: '#6D4C41'
            });
        })
        .finally(() => {
            // Reset button state
            confirmButton.disabled = false;
            confirmButton.innerHTML = originalText;
        });
    });
} 

// --- Add Your Orders Tab to Food Menu Modal ---
// (Function and event listener removed)

function renderCategoryBar() {
  // Render the category bar with 'Your Orders' right-aligned
  const categories = ['All', 'Rice Meals', 'Burgers', 'Desserts', 'Beverages'];
  let catHtml = '<div class="d-flex justify-content-between align-items-center mb-3" id="food-category-bar">';
  catHtml += '<div>';
  categories.forEach(cat => {
    catHtml += `<button class="food-cat-btn" data-cat="${cat}">${cat}</button> `;
  });
  catHtml += '</div>';
  catHtml += '<button class="food-cat-btn ms-3" id="yourOrdersCatBtn" data-cat="Your Orders" style="cursor: pointer;">Your Orders</button>';
  catHtml += '</div>';
  
  // Ensure the Your Orders button has proper event handling
  setTimeout(() => {
    const yourOrdersBtn = document.getElementById('yourOrdersCatBtn');
    if (yourOrdersBtn) {
      console.log('Your Orders button found, ensuring event listener is attached');
      
      // Remove any existing event listeners to prevent duplicates
      yourOrdersBtn.removeEventListener('click', handleYourOrdersClick);
      yourOrdersBtn.removeEventListener('click', handleYourOrdersClickDirect);
      
      // Add the event listener directly to the button for immediate response
      yourOrdersBtn.addEventListener('click', handleYourOrdersClickDirect);
      
      // Also add a click handler using onclick for extra reliability
      yourOrdersBtn.onclick = function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log('Your Orders button clicked (onclick handler)!');
        
        // Remove 'active' from all category buttons
        document.querySelectorAll('.food-cat-btn').forEach(btn => btn.classList.remove('active'));
        // Set 'active' on this button
        this.classList.add('active');
        // Load order history
        loadYourOrders();
      };
      
      // Test the button to make sure it's clickable
      console.log('Your Orders button is now ready for clicks');
    } else {
      console.error('Your Orders button not found after timeout!');
    }
  }, 100);
  
  // Additional check after a longer delay to ensure button is properly set up
  setTimeout(() => {
    const yourOrdersBtn = document.getElementById('yourOrdersCatBtn');
    if (yourOrdersBtn) {
      console.log('Final check: Your Orders button is present and should be clickable');
      // Force ensure events are attached
      ensureYourOrdersButtonEvents();
    }
  }, 500);
  
  return catHtml;
}

function loadYourOrders() {
  console.log('=== LOAD YOUR ORDERS FUNCTION CALLED ===');
  console.log('Function started successfully');
  
  const content = document.getElementById('food-menu-content');
  console.log('Food menu content element:', content);
  
  if (!content) {
    console.error('Food menu content element not found!');
    return;
  }
  
  // Check if we're coming from the main menu or directly from View Orders
  const isFromMainMenu = document.querySelector('.food-cat-btn.active') !== null;
  console.log('Is from main menu:', isFromMainMenu);
  
  // Hide the category bar if present
  const categoryBar = document.getElementById('food-category-bar');
  if (categoryBar) {
    categoryBar.style.display = 'none';
    console.log('Category bar hidden');
  } else {
    console.log('Category bar not found');
  }
  
  // Show Back to Menu button
   let backBtnHtml = `<div style="margin-bottom:14px;"><button id="backToMenuBtn" type="button" style="background:none;border:none;padding:0;margin:0;font-size:1.18em;font-weight:600;cursor:pointer;display:flex;align-items:center;white-space:nowrap;color:inherit;"><span style='font-size:1.18em;margin-right:10px;font-weight:600;'>&#8592;</span><span style='font-size:1.18em;font-weight:600;'>Back to Menu</span></button></div>`;
   content.innerHTML = backBtnHtml + '<div id="order-history-list"><div class="text-center text-muted"><i class="fas fa-spinner fa-spin me-2"></i>Loading your orders...</div></div>';
  
  // Ensure modal backdrop is visible for Your Orders view
  const modal = document.getElementById('foodMenuModal');
  if (modal && typeof bootstrap !== 'undefined') {
    const modalInstance = bootstrap.Modal.getInstance(modal);
    if (modalInstance) {
      // Use the helper function to ensure backdrop is visible
      if (typeof ensureModalBackdrop === 'function') {
        ensureModalBackdrop();
      } else {
        // Fallback if helper function is not available
        let backdrop = document.querySelector('.modal-backdrop');
      if (!backdrop) {
          backdrop = document.createElement('div');
          backdrop.className = 'modal-backdrop fade show';
          document.body.appendChild(backdrop);
        }
      document.body.classList.add('modal-open');
      }
    }
  }
  
  // Add event listener for Back to Menu button
  setTimeout(() => {
    const backBtn = document.getElementById('backToMenuBtn');
    if (backBtn) {
      backBtn.onclick = function() {
        // Restore original modal title
        const modalTitle = document.querySelector('#foodMenuModal .modal-title');
        if (modalTitle) {
          modalTitle.textContent = 'Food Menu';
        }
        
        // Show the category bar again
        const catBar = document.getElementById('food-category-bar');
        if (catBar) catBar.style.display = '';
        // Show the menu/categories view
        if (typeof showFoodMenuModal === 'function') {
          showFoodMenuModal();
        }
        // Ensure backdrop is maintained when returning to menu
        setTimeout(() => {
          if (typeof ensureModalBackdrop === 'function') {
            ensureModalBackdrop();
          }
        }, 100);
      };
    }
    
    // Also add a close button to the orders view
    const ordersContent = document.getElementById('ordersContent');
    if (ordersContent) {
      const closeBtnHtml = `<div style="text-align: right; margin-bottom: 10px;">
        <button type="button" class="btn btn-secondary btn-sm" onclick="closeFoodMenuModal()">
          <i class="fas fa-times"></i> Close
        </button>
      </div>`;
      ordersContent.insertAdjacentHTML('afterbegin', closeBtnHtml);
    }
  }, 0);
  // Now render the order history
  fetch('/api/food-order-history')
    .then(res => res.json())
    .then(data => {
      // Ensure backdrop is maintained after content loads
      setTimeout(() => {
        if (typeof ensureModalBackdrop === 'function') {
          ensureModalBackdrop();
        }
      }, 200);
      
      if (!data.success) {
        document.getElementById('order-history-list').innerHTML = '<div class="text-center text-danger">Failed to load your orders.</div>';
        return;
      }
      if (!Array.isArray(data.orders) || data.orders.length === 0) {
        document.getElementById('order-history-list').innerHTML = '<div class="text-center text-muted">No food orders found.</div>';
        return;
      }
      let html = '<div class="order-history-grid">';
      data.orders.forEach(order => {
        const foodServiceIp = window.FOOD_SERVICE_IP || '192.168.1.12';
        console.log("Food Service IP from JS:", foodServiceIp);
        // Handle case where foodServiceIp might be "None" string
        const validIp = (foodServiceIp && foodServiceIp !== 'None' && foodServiceIp !== 'null') ? foodServiceIp : '192.168.1.12';
        const receiptUrl = `http://${validIp}/online-food-ordering/print_receipt.php?order_id=${order.id}`;
        // Determine status class
        let statusClass = '';
        let statusText = (order.status || '').toLowerCase();
        if (statusText === 'completed') statusClass = 'order-status-completed';
        else if (statusText === 'pending') statusClass = 'order-status-pending';
        else if (statusText === 'processing') statusClass = 'order-status-processing';
        else if (statusText === 'cancelled' || statusText === 'rejected') statusClass = 'order-status-cancelled';
        else statusClass = 'order-status-pending';
        // Capitalize first letter of status for display
        const displayStatus = order.status ? order.status.charAt(0).toUpperCase() + order.status.slice(1).toLowerCase() : '';
        
        // Get menu_item_id from various sources with fallbacks
        let menuItemId = order.menu_item_id || 0;
        
        // Fallback 1: Check if it's directly in the order object
        if ((!menuItemId || menuItemId === 0) && order.menu_item_id) {
          menuItemId = parseInt(order.menu_item_id);
        }
        
        // Fallback 2: Check the items array if available
        if ((!menuItemId || menuItemId === 0) && order.items && order.items.length > 0) {
          for (let i = 0; i < order.items.length; i++) {
            if (order.items[i].menu_item_id && parseInt(order.items[i].menu_item_id) > 0) {
              menuItemId = parseInt(order.items[i].menu_item_id);
              break;
            }
          }
        }
        
        // For debugging
        console.log(`Order #${order.id}: menu_item_id = ${menuItemId}`);
        
        // For completed orders, show either the rate button or the static rating
        let ratingHtml = '';
        if (order.status && order.status.toLowerCase() === 'completed') {
          // Always show the rate/edit button
          let ratingIdAttr = '';
          if (order.has_rating && order.rating_id) {
            ratingIdAttr = `data-rating-id=\"${order.rating_id}\"`;
          }
          ratingHtml = `
            <button class="btn btn-rate-order full-width-rate" 
                    onclick="rateOrder(${order.id || 0}, ${menuItemId || 0})" 
                    data-order-id="${order.id || 0}" 
                    data-menu-item-id="${menuItemId || 0}" 
                    ${ratingIdAttr}>
                <i class='fas fa-star'></i> ${order.has_rating ? 'Edit Rating' : 'Rate'}
            </button>
          `;
        }
        
        html += `<div class="order-history-tile" data-order-id="${order.id}" data-menu-item-id="${menuItemId || 0}">
          <div class="mb-2"><strong>Order #${order.id || ''}</strong> - ${order.created_at || ''}</div>
          <div><span>Status: </span><span class="order-status-badge ${statusClass}">${displayStatus}</span></div>
          <div>Total: ₱${order.total_amount || ''}</div>
          <div class="order-history-actions">
            <a class="btn btn-sm btn-primary" href="${receiptUrl}" target="_blank" download>View/Download Receipt</a>
            ${order.status && (order.status.toLowerCase() === 'pending' || order.status.toLowerCase() === 'processing') ? `<button class="btn btn-cancel-order" onclick="cancelOrder(${order.id || 0}, this)">Cancel</button>` : ''}
            ${order.status && (order.status.toLowerCase() !== 'pending' && order.status.toLowerCase() !== 'processing') ? `<button class="btn btn-sm btn-danger" onclick="deleteOrder(${order.id || 0}, this)">Delete</button>` : ''}
            ${ratingHtml}
          </div>
        </div>`;
      });
      html += '</div>';
      document.getElementById('order-history-list').innerHTML = html;
    })
    .catch(() => {
      document.getElementById('order-history-list').innerHTML = '<div class="text-center text-danger">Failed to load your orders.</div>';
    });
}

function deleteOrder(orderId, btn) {
  if (!confirm('Delete this order?')) return;
  btn.disabled = true;
  const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
  fetch(`/api/delete-food-order/${orderId}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken
    }
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        // Remove the order card (order-history-tile) from the UI
        let card = btn.closest('.order-history-tile');
        if (card) card.remove();
      } else {
        alert('Failed to delete order.');
        btn.disabled = false;
      }
    })
    .catch(() => {
      alert('Failed to delete order.');
      btn.disabled = false;
    });
}

// Add cancelOrder function
function cancelOrder(orderId, btn) {
  // Prompt for cancellation reason
  const cancellationReason = prompt('Please provide a reason for cancelling this order:');
  if (cancellationReason === null) return; // User clicked Cancel
  
  if (!cancellationReason.trim()) {
    alert('Please provide a reason for cancellation.');
    return;
  }
  
  if (!confirm('Cancel this order?')) return;
  btn.disabled = true;
  const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
  fetch(`/api/cancel-food-order/${orderId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({
      cancellation_reason: cancellationReason.trim()
    })
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        // Update status to cancelled and remove the cancel button
        let card = btn.closest('.order-history-tile');
        if (card) {
          let statusDiv = card.querySelector('.order-status-badge');
          if (statusDiv) {
            statusDiv.textContent = 'Cancelled';
            statusDiv.classList.remove('order-status-pending', 'order-status-processing', 'order-status-completed');
            statusDiv.classList.add('order-status-cancelled');
          }
        btn.remove();
          // Re-render the Delete button if not present
          let actionsDiv = card.querySelector('.order-history-actions');
          if (actionsDiv && !actionsDiv.querySelector('.btn-danger')) {
            const orderId = card.querySelector('.order-status-badge').closest('.order-history-tile').querySelector('.mb-2').textContent.match(/Order #(\d+)/)[1];
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'btn btn-sm btn-danger';
            deleteBtn.textContent = 'Delete';
            deleteBtn.onclick = function() { deleteOrder(orderId, deleteBtn); };
            actionsDiv.appendChild(deleteBtn);
          }
        }
      } else {
        alert(data.message || 'Failed to cancel order.');
        btn.disabled = false;
      }
    })
    .catch(() => {
      alert('Failed to cancel order.');
      btn.disabled = false;
    });
}

function rateOrder(orderId, menuItemId) {
  // Try to get the rating id from the button
  const orderTile = document.querySelector(`.order-history-tile[data-order-id='${orderId}']`);
  let ratingId = null;
  if (orderTile) {
    const rateBtn = orderTile.querySelector('.btn-rate-order');
    if (rateBtn && rateBtn.getAttribute('data-rating-id')) {
      ratingId = rateBtn.getAttribute('data-rating-id');
    }
  }
  if (ratingId) {
    fetch(`/api/eatnrun-rating?id=${ratingId}`)
      .then(res => res.json())
      .then(data => {
        if (data && data.success && data.rating) {
          showRateOrderModal(orderId, menuItemId, data.rating);
        } else {
          showRateOrderModal(orderId, menuItemId, {});
        }
      })
      .catch(() => {
        showRateOrderModal(orderId, menuItemId, {});
      });
  } else {
    showRateOrderModal(orderId, menuItemId, {});
  }
}

// Helper function to get a default menu item and continue with rating
function getDefaultMenuItem(orderId) {
  fetch('/api/get-default-menu-item.php')
    .then(res => res.json())
    .then(data => {
      if (data.success && data.menu_item_id) {
        console.log(`Using default menu item ID ${data.menu_item_id} for order ${orderId}`);
        const menuItemId = data.menu_item_id;
        
        // Update the order with this menu item ID
        fetch('/api/update-order-menu-item', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
          },
          body: JSON.stringify({
            order_id: orderId,
            menu_item_id: menuItemId
          })
        });
        
        fetchRatingAndShowModal(orderId, menuItemId);
      } else {
        console.error("Could not get default menu item, using ID 1");
        fetchRatingAndShowModal(orderId, 1);
      }
    })
    .catch(err => {
      console.error("Error fetching default menu item:", err);
      fetchRatingAndShowModal(orderId, 1);
    });
}

function fetchRatingAndShowModal(orderId, menuItemId) {
  // Try to get the rating id from the button
  const orderTile = document.querySelector(`.order-history-tile[data-order-id='${orderId}']`);
  let ratingId = null;
  if (orderTile) {
    const rateBtn = orderTile.querySelector('.btn-rate-order');
    if (rateBtn && rateBtn.getAttribute('data-rating-id')) {
      ratingId = rateBtn.getAttribute('data-rating-id');
    }
  }
  if (ratingId) {
    fetch(`/api/eatnrun-rating?id=${ratingId}`)
      .then(res => res.json())
      .then(data => {
        if (data && data.success && data.rating) {
          showRateOrderModal(orderId, menuItemId, data.rating);
        } else {
          showRateOrderModal(orderId, menuItemId, {});
        }
      })
      .catch(() => {
        showRateOrderModal(orderId, menuItemId, {});
      });
  } else {
    showRateOrderModal(orderId, menuItemId, {});
  }
}

function showRateOrderModal(orderId, menuItemId, existingRating) {
  // If menuItemId is still 0, use a default value instead of showing an error
  if (!menuItemId || menuItemId === 0) {
    console.warn(`Using default menu_item_id for order ${orderId} as none could be found`);
    // Use 1 as a default menu_item_id to allow rating to proceed
    menuItemId = 1;
  }

  // Check if the container exists, if not create it
  let container = document.getElementById('ratingsModalContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'ratingsModalContainer';
    document.body.appendChild(container);
  }
  
  // Add star rating CSS if not already added
  if (!document.getElementById('starRatingStyles')) {
    const style = document.createElement('style');
    style.id = 'starRatingStyles';
    style.innerHTML = `
      .star-rating {
        display: flex;
        flex-direction: row-reverse;
        justify-content: center;
        font-size: 1.5em;
      }
      .star-rating input {
        display: none;
      }
      .star-rating label {
        color: #ddd;
        cursor: pointer;
        padding: 0 0.1em;
      }
      .star-rating label:before {
        content: '\u2605';
      }
      .star-rating input:checked ~ label,
      .star-rating label:hover,
      .star-rating label:hover ~ label {
        color: #f90;
      }
      .star-rating.readonly label {
        cursor: default;
      }
      .star-rating.readonly label:hover,
      .star-rating.readonly label:hover ~ label {
        color: #ddd;
      }
      .star-rating.readonly input:checked ~ label {
        color: #f90;
      }
      .rate-order-comment-box {
        border: 1px solid #ccc;
        border-radius: 4px;
        padding: 8px;
        font-family: inherit;
      }
      #rateOrderSubmitBtn {
        background-color: #6D4C41;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        margin-right: 8px;
      }
      #closeRateOrderModal {
        background-color: #f1f1f1;
        border: 1px solid #ccc;
        border-radius: 4px;
        cursor: pointer;
      }
      .success-modal {
        background: #fff;
        padding: 32px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 24px rgba(0,0,0,0.18);
      }
      .success-modal i {
        font-size: 48px;
        color: #4CAF50;
        margin-bottom: 16px;
      }
      .success-modal h2 {
        color: #333;
        margin-bottom: 16px;
      }
      .success-modal button {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 24px;
        cursor: pointer;
        font-size: 1em;
      }
    `;
    document.head.appendChild(style);
  }
  
  container.innerHTML = '';
  container.style.display = 'flex';
  container.style.position = 'fixed';
  container.style.top = '0';
  container.style.left = '0';
  container.style.width = '100vw';
  container.style.height = '100vh';
  container.style.background = 'rgba(0,0,0,0.5)';
  container.style.zIndex = '99999';
  container.style.alignItems = 'center';
  container.style.justifyContent = 'center';
  container.style.backdropFilter = 'blur(2px)';

  let modal = document.createElement('div');
  modal.style.background = '#fff';
  modal.style.padding = '32px';
  modal.style.borderRadius = '12px';
  modal.style.boxShadow = '0 8px 32px rgba(0,0,0,0.25)';
  modal.style.maxWidth = '400px';
  modal.style.width = '90%';
  modal.style.maxHeight = '90vh';
  modal.style.overflowY = 'auto';
  modal.style.transform = 'scale(0.9)';
  modal.style.transition = 'transform 0.3s ease-out';

  // Always show editable form, pre-fill if editing
  const isEditing = existingRating && existingRating.id;
  const prefillRating = existingRating && existingRating.rating ? existingRating.rating : 0;
  const prefillComment = existingRating && existingRating.comment ? existingRating.comment : '';
  const ratingId = isEditing ? existingRating.id : null;

  modal.innerHTML = `
    <h2 style="margin-bottom:16px;">Rate Your Order</h2>
    <div class="star-rating" style="margin-bottom:18px;">
      <input type="radio" id="star5" name="rating" value="5" ${prefillRating == 5 ? 'checked' : ''}><label for="star5" title="5 stars"></label>
      <input type="radio" id="star4" name="rating" value="4" ${prefillRating == 4 ? 'checked' : ''}><label for="star4" title="4 stars"></label>
      <input type="radio" id="star3" name="rating" value="3" ${prefillRating == 3 ? 'checked' : ''}><label for="star3" title="3 stars"></label>
      <input type="radio" id="star2" name="rating" value="2" ${prefillRating == 2 ? 'checked' : ''}><label for="star2" title="2 stars"></label>
      <input type="radio" id="star1" name="rating" value="1" ${prefillRating == 1 ? 'checked' : ''}><label for="star1" title="1 star"></label>
    </div>
    <textarea class="rate-order-comment-box" maxlength="100" rows="4" style="width:300px;height:100px;font-size:1.1em;" placeholder="Share your experience...">${prefillComment}</textarea>
    <div style="text-align:right;font-size:0.97em;color:#a08b7b;margin-bottom:18px;">
      <span id="rateOrderWordCount">${prefillComment.length}</span>/100 words
    </div>
    <button id="rateOrderSubmitBtn" style="margin-top:16px;padding:8px 18px;font-size:1em;">${isEditing ? 'Update Review' : 'Submit Review'}</button>
    <button id="closeRateOrderModal" style="margin-top:16px;padding:8px 18px;font-size:1em;">Close</button>
  `;
  container.appendChild(modal);
  
  // Add entrance animation
  setTimeout(() => {
    modal.style.transform = 'scale(1)';
  }, 10);

  // Set up event handlers
  const commentBox = container.querySelector('.rate-order-comment-box');
  commentBox.oninput = function() {
    container.querySelector('#rateOrderWordCount').textContent = commentBox.value.length;
  };
  setTimeout(() => { commentBox.focus(); }, 50);

  // Star rating logic
  let selectedRating = prefillRating;
  const starInputs = container.querySelectorAll('.star-rating input[type="radio"]');
  starInputs.forEach(input => {
    input.onclick = function() {
      selectedRating = parseInt(input.value);
    };
  });

  // Submit logic
  container.querySelector('#rateOrderSubmitBtn').onclick = function() {
    if (!selectedRating) {
      alert('Please select a rating.');
      return;
    }
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    let payload = { rating: selectedRating, comment: commentBox.value };
    let method = 'POST';
    if (existingRating && existingRating.id) {
      payload = { id: existingRating.id, rating: selectedRating, comment: commentBox.value };
      method = 'PUT';
    } else {
      payload.order_id = orderId;
    }
    fetch('/api/eatnrun-rating', {
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
      // Show success modal
      modal.innerHTML = `
        <div class=\"success-modal\" style=\"background:#fff;border-radius:16px;box-shadow:0 4px 24px rgba(109,76,65,0.18);padding:32px 24px;text-align:center;max-width:340px;margin:0 auto;\">\n        <i class=\"fas fa-check-circle\" style=\"color:#6D4C41;font-size:3.2em;margin-bottom:12px;\"></i>\n        <h2 style=\"color:#6D4C41;margin-bottom:10px;\">${existingRating && existingRating.id ? 'Review Updated!' : 'Rated Successfully!'}</h2>\n        <p style=\"color:#6D4C41;margin-bottom:24px;\">Thank you for your feedback!</p>\n        <button id="closeSuccessModalBtn" style=\"background:#6D4C41;color:#fff;border:none;border-radius:8px;padding:10px 32px;font-size:1.1em;font-weight:600;box-shadow:0 2px 8px rgba(109,76,65,0.10);transition:background 0.2s;\">Close</button>\n      </div>\n    `;
      // When the user closes the modal, hide it and reload the order history
      container.querySelector('#closeSuccessModalBtn').onclick = function() {
        container.style.display = 'none';
        container.innerHTML = '';
        loadYourOrders(); // Refresh the order history
      };
    });
  };

  // Close button logic
  container.querySelector('#closeRateOrderModal').onclick = function() {
    container.style.display = 'none';
    container.innerHTML = '';
  };
}

// Add the tab when the food menu modal is shown
const foodMenuModalEl2 = document.getElementById('foodMenuModal');
if (foodMenuModalEl2) {
  foodMenuModalEl2.addEventListener('show.bs.modal', addYourOrdersTab);
  
  // Simple modal cleanup when hidden
  foodMenuModalEl2.addEventListener('hidden.bs.modal', function() {
    // Basic cleanup without interfering with Bootstrap
    const foodMenuContent = document.getElementById('food-menu-content');
    if (foodMenuContent) {
      foodMenuContent.innerHTML = '<div class="text-center text-muted"><i class="fas fa-spinner fa-spin me-2"></i>Loading menu...</div>';
    }
  });
}

// After rendering the Delivery Details form, add this event handler:
setTimeout(() => {
  const backBtn = document.getElementById('backFromDeliveryDetailsBtn');
  if (backBtn) {
    backBtn.onclick = function() {
      // Close the food menu modal
      const foodMenuModal = document.getElementById('foodMenuModal');
      if (foodMenuModal && typeof bootstrap !== 'undefined') {
        const modalInstance = bootstrap.Modal.getInstance(foodMenuModal);
        if (modalInstance) modalInstance.hide();
      }
    };
  }
}, 0); 

// Hook up 'View Orders' menu item to open Food Menu modal and show order history directly
document.addEventListener('click', function(e) {
    const anchor = e.target.closest('#viewOrdersMenuItem');
    if (!anchor) return;
    
    console.log('View Orders clicked!'); // Debug log
    e.preventDefault();

    // Open the food menu modal
    const foodMenuModalEl = document.getElementById('foodMenuModal');
    console.log('Food menu modal element:', foodMenuModalEl); // Debug log
    
    if (foodMenuModalEl && typeof bootstrap !== 'undefined') {
        console.log('Opening modal with Bootstrap...'); // Debug log
        const modal = new bootstrap.Modal(foodMenuModalEl);
        modal.show();
        
        // Wait for modal to be fully shown, then directly load orders without showing menu first
        foodMenuModalEl.addEventListener('shown.bs.modal', function onModalShown() {
            // Remove this event listener to prevent multiple calls
            foodMenuModalEl.removeEventListener('shown.bs.modal', onModalShown);
            
            // Update modal title to reflect we're viewing orders
            const modalTitle = foodMenuModalEl.querySelector('.modal-title');
            if (modalTitle) {
                modalTitle.textContent = 'Your Orders';
            }
            
            // Show loading state first
            const foodMenuContent = document.getElementById('food-menu-content');
            if (foodMenuContent) {
                foodMenuContent.innerHTML = '<div class="text-center text-muted" style="padding: 40px;"><i class="fas fa-spinner fa-spin fa-2x mb-3"></i><br>Loading your orders...</div>';
            }
            
            // Directly load orders without going through the menu
            if (typeof loadYourOrders === 'function') {
                console.log('Directly calling loadYourOrders function...'); // Debug log
                // Small delay to show loading state
                setTimeout(() => {
                    loadYourOrders();
                }, 300);
            } else {
                console.log('loadYourOrders function not found'); // Debug log
                // Fallback: try to find and click the Your Orders button
        setTimeout(() => {
            const yourOrdersBtn = document.getElementById('yourOrdersCatBtn');
            if (yourOrdersBtn) {
                console.log('Found yourOrdersCatBtn, clicking it...'); // Debug log
                yourOrdersBtn.click();
            }
                }, 100);
            }
        }, { once: true }); // Use once option to ensure it only runs once
    } else {
        console.log('Modal element not found or Bootstrap not available!'); // Debug log
        alert('Food menu modal not available on this page.');
    }
});

// Floating Action Button for Food Ordering
document.addEventListener('DOMContentLoaded', function() {
    const orderFoodBtn = document.getElementById('orderFoodBtn');
    
    if (orderFoodBtn) {
        console.log('Floating button found and event listener added');
        orderFoodBtn.addEventListener('click', function() {
            console.log('Floating button clicked!');
            
            // Open modal directly with proper Bootstrap handling for smooth animations
                const foodMenuModal = document.getElementById('foodMenuModal');
            console.log('Food menu modal element:', foodMenuModal);
            
                if (foodMenuModal && typeof bootstrap !== 'undefined') {
                console.log('Opening modal with Bootstrap...');
                
                // Debug: Check current modal state
                console.log('Modal fade class:', foodMenuModal.classList.contains('fade'));
                console.log('Modal show class:', foodMenuModal.classList.contains('show'));
                console.log('Modal display:', foodMenuModal.style.display);
                
                // Ensure animations are properly set up before showing
                if (typeof ensureDashboardFloatingButtonAnimations === 'function') {
                    ensureDashboardFloatingButtonAnimations();
                } else if (typeof ensureModalAnimations === 'function') {
                    ensureModalAnimations();
                }
                
                // Force animation setup for dashboard
                foodMenuModal.classList.add('fade');
                foodMenuModal.offsetHeight; // Force reflow
                
                    const modal = new bootstrap.Modal(foodMenuModal);
                    modal.show();
                
                // After modal is shown, load the menu content
                foodMenuModal.addEventListener('shown.bs.modal', function onModalShown() {
                    // Remove this event listener to prevent multiple calls
                    foodMenuModal.removeEventListener('shown.bs.modal', onModalShown);
                    
                    // Small delay to ensure animations are visible
                    setTimeout(() => {
                        // Load the menu content
                        if (typeof showFoodMenuModal === 'function') {
                            console.log('Loading menu content...');
                            showFoodMenuModal(true); // Skip cleanup to preserve animations
                        }
                    }, 100);
                }, { once: true });
                } else {
                console.log('Modal element not found or Bootstrap not available!');
                alert('Food menu modal not available on this page.');
            }
        });
    } else {
        console.log('Floating button not found!');
    }
});

// Function to close the food menu modal from any state
function closeFoodMenuModal() {
  const foodMenuModal = document.getElementById('foodMenuModal');
  if (foodMenuModal) {
    // Use Bootstrap's natural closing mechanism
    const modal = bootstrap.Modal.getInstance(foodMenuModal);
    if (modal) {
      modal.hide();
    } else {
      // If no instance exists, trigger the close button click
      const closeBtn = foodMenuModal.querySelector('.btn-close');
      if (closeBtn) {
        closeBtn.click();
      }
    }
  }
}

// Force cleanup function to remove stuck modal backdrops
function forceCleanupModals() {
  // Remove all modal backdrops
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
  
  // Remove modal-open class from body
  document.body.classList.remove('modal-open');
  
  // Remove any inline styles that Bootstrap added
  document.body.style.removeProperty('padding-right');
  document.body.style.removeProperty('overflow');
  
  // Reset any modal elements
  const foodMenuModal = document.getElementById('foodMenuModal');
  if (foodMenuModal) {
    foodMenuModal.classList.remove('show');
    foodMenuModal.style.display = 'none';
    foodMenuModal.setAttribute('aria-hidden', 'true');
    foodMenuModal.removeAttribute('aria-modal');
    foodMenuModal.removeAttribute('role');
  }
  
  // Reset modal content
  const foodMenuContent = document.getElementById('food-menu-content');
  if (foodMenuContent) {
    foodMenuContent.innerHTML = '<div class="text-center text-muted"><i class="fas fa-spinner fa-spin me-2"></i>Loading menu...</div>';
  }
}

// Helper function to ensure backdrop is always visible
function ensureModalBackdrop() {
  let backdrop = document.querySelector('.modal-backdrop');
  if (!backdrop) {
    backdrop = document.createElement('div');
    backdrop.className = 'modal-backdrop fade show';
    document.body.appendChild(backdrop);
  }
  document.body.classList.add('modal-open');
}

// Enhanced backdrop monitoring function
function monitorModalBackdrop() {
  const modal = document.getElementById('foodMenuModal');
  if (modal && modal.classList.contains('show')) {
    // Check if backdrop exists and is visible
    let backdrop = document.querySelector('.modal-backdrop');
    if (!backdrop || !backdrop.classList.contains('show')) {
      ensureModalBackdrop();
    }
    
    // Ensure body has modal-open class
    if (!document.body.classList.contains('modal-open')) {
      document.body.classList.add('modal-open');
    }
  }
}

// Function to ensure modal animations work properly
function ensureModalAnimations() {
  const modal = document.getElementById('foodMenuModal');
  if (modal) {
    // Ensure fade class is present
    if (!modal.classList.contains('fade')) {
      modal.classList.add('fade');
    }
    
    // Force reflow to ensure animations work
    modal.offsetHeight;
    
    // Ensure proper transition timing
    modal.style.transition = 'opacity 0.15s linear';
    
    // Ensure modal dialog has proper transitions
    const dialog = modal.querySelector('.modal-dialog');
    if (dialog) {
      dialog.style.transition = 'transform 0.3s ease-out';
    }
    
    // Check if backdrop has proper transitions
    const backdrop = document.querySelector('.modal-backdrop');
    if (backdrop) {
      backdrop.style.transition = 'opacity 0.15s linear';
    } else {
      // Create backdrop if it doesn't exist
      const newBackdrop = document.createElement('div');
      newBackdrop.className = 'modal-backdrop fade';
      document.body.appendChild(newBackdrop);
    }
  }
}

// Dashboard-specific function to ensure floating button animations work
function ensureDashboardFloatingButtonAnimations() {
  const modal = document.getElementById('foodMenuModal');
  if (modal) {
    // Force dashboard-specific animation setup
    modal.style.transition = 'opacity 0.15s linear !important';
    
    const dialog = modal.querySelector('.modal-dialog');
    if (dialog) {
      dialog.style.transition = 'transform 0.3s ease-out !important';
      dialog.style.transform = 'translate(0, -50px)';
    }
    
    // Ensure backdrop has proper transitions
    let backdrop = document.querySelector('.modal-backdrop');
    if (!backdrop) {
      backdrop = document.createElement('div');
      backdrop.className = 'modal-backdrop fade';
      document.body.appendChild(backdrop);
    }
    backdrop.style.transition = 'opacity 0.15s linear !important';
  }
}

// Make cleanup functions available globally
window.closeFoodMenuModal = closeFoodMenuModal;
window.forceCleanupModals = forceCleanupModals;
window.ensureModalBackdrop = ensureModalBackdrop;
window.monitorModalBackdrop = monitorModalBackdrop;
window.ensureModalAnimations = ensureModalAnimations;
window.ensureDashboardFloatingButtonAnimations = ensureDashboardFloatingButtonAnimations;



// Improved modal handling to prevent stuck modals
document.addEventListener('DOMContentLoaded', function() {
  const foodMenuModal = document.getElementById('foodMenuModal');
  
  if (foodMenuModal) {
    // Ensure proper modal cleanup on all events
    foodMenuModal.addEventListener('show.bs.modal', function() {
      // Reset modal state when opening
      this.classList.remove('fade');
      this.style.display = 'block';
    });
    
    foodMenuModal.addEventListener('shown.bs.modal', function() {
      // Ensure modal is properly displayed
      this.classList.add('show');
      this.style.display = 'block';
    });
    
    foodMenuModal.addEventListener('hide.bs.modal', function() {
      // Prepare for hiding
      this.classList.remove('show');
    });
    
    foodMenuModal.addEventListener('hidden.bs.modal', function() {
      // Complete cleanup when hidden
      this.style.display = 'none';
      this.classList.remove('show');
      
      // Remove any lingering backdrop
      document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
      document.body.classList.remove('modal-open');
      document.body.style.removeProperty('padding-right');
      document.body.style.removeProperty('overflow');
    });
  }
});

// Global safety net: remove any lingering Bootstrap modal backdrop/state on navigation or page restore
(function() {
  function cleanupModalArtifacts() {
    try {
      // Close the food menu modal if it's somehow visible
      const foodMenuModal = document.getElementById('foodMenuModal');
      if (foodMenuModal && foodMenuModal.classList.contains('show') && typeof bootstrap !== 'undefined') {
        const instance = bootstrap.Modal.getInstance(foodMenuModal) || bootstrap.Modal.getOrCreateInstance(foodMenuModal);
        instance.hide();
      }
    } catch (e) {}

    // Remove any lingering backdrops and body state
    document.querySelectorAll('.modal-backdrop').forEach(function(el) { el.remove(); });
    document.body.classList.remove('modal-open');
    document.body.style.removeProperty('padding-right');
    document.body.style.removeProperty('overflow');
  }

  // Run immediately on script load and standard lifecycle events
  cleanupModalArtifacts();
  window.addEventListener('load', cleanupModalArtifacts, { once: true });
  window.addEventListener('pageshow', cleanupModalArtifacts); // handles bfcache restores (back/forward)
  window.addEventListener('popstate', cleanupModalArtifacts);
  document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'visible') {
      cleanupModalArtifacts();
    }
  });
  
  // Watchdog: remove backdrops if no modal is actually open
  window.__modalIsOpen = false;
  document.addEventListener('show.bs.modal', function(){ window.__modalIsOpen = true; }, true);
  document.addEventListener('hidden.bs.modal', function(){ window.__modalIsOpen = false; }, true);
  function hasOpenBootstrapModal() {
    if (window.__modalIsOpen) return true;
    return !!document.querySelector('.modal.show, .modal[aria-modal="true"], .modal[style*="display: block"]');
  }
  function removeOrphanBackdrops() {
    // Never touch backdrop while a modal is opening/open
    if (!hasOpenBootstrapModal()) {
      document.querySelectorAll('.modal-backdrop').forEach(function(el) { el.remove(); });
      document.body.classList.remove('modal-open');
      document.body.style.removeProperty('padding-right');
      document.body.style.removeProperty('overflow');
    }
  }
  // Run shortly after load to catch late script-inserted backdrops
  let watchdogRuns = 0;
  const watchdogTimer = setInterval(function() {
    watchdogRuns++;
    removeOrphanBackdrops();
    if (watchdogRuns > 8) { // ~4s at 500ms and then stop
      clearInterval(watchdogTimer);
    }
  }, 500);
  // Remove aggressive DOM observer to avoid fighting Bootstrap
})();

// Notification modal: enable backdrop click-to-close and add animations
document.addEventListener('DOMContentLoaded', function() {
  const notifModal = document.getElementById('notificationDetailsModal');
  if (!notifModal) return;

  // Inject simple scale/fade animations once
  (function injectNotifAnimCSS(){
    if (document.getElementById('notif-anim-styles')) return;
    const css = document.createElement('style');
    css.id = 'notif-anim-styles';
    css.textContent = `
      .notif-anim .modal-dialog {
        transition: transform 220ms cubic-bezier(0.22, 1, 0.36, 1), opacity 220ms linear, box-shadow 220ms ease;
        transform: translateY(8px) scale(0.98);
        opacity: 0;
        will-change: transform, opacity;
      }
      .notif-anim.modal.show .modal-dialog {
        transform: translateY(0) scale(1);
        opacity: 1;
        box-shadow: 0 16px 40px rgba(0,0,0,0.25);
      }
    `;
    document.head.appendChild(css);
  })();

  // Ensure Bootstrap fade class and our animation class
  notifModal.classList.add('fade', 'notif-anim');

  // Click on backdrop (outside dialog) closes modal
  notifModal.addEventListener('click', function(e) {
    if (e.target === notifModal) {
      try {
        if (typeof bootstrap !== 'undefined') {
          const instance = bootstrap.Modal.getInstance(notifModal) || bootstrap.Modal.getOrCreateInstance(notifModal);
          instance.hide();
        }
      } catch (err) {}
    }
  });

  // Keyboard escape is default, ensure it's enabled
  try {
    if (typeof bootstrap !== 'undefined') {
      bootstrap.Modal.getOrCreateInstance(notifModal, { backdrop: true, keyboard: true, focus: true });
    }
  } catch (err) {}
});

// Cart System - Global Variables
let cart = [];
let cartTotal = 0;

// Cart Functions
// AUTO-COMPUTATION: The cart automatically calculates totals whenever quantities change
// This includes: adding items, changing quantities, removing items, and clearing cart
function addToCart(item) {
    console.log('addToCart called with item:', item);
    console.log('Current cart before adding:', cart);
    
    const existingItem = cart.find(cartItem => cartItem.id === item.id);
    
    if (existingItem) {
        console.log('Item already exists, incrementing quantity from', existingItem.quantity, 'to', existingItem.quantity + 1);
        if (existingItem.quantity >= 99) {
            showCartNotification('Maximum quantity limit is 99!');
            return;
        }
        existingItem.quantity += 1;
    } else {
        console.log('Adding new item to cart:', item);
        cart.push({
            ...item,
            quantity: 1
        });
    }
    
    console.log('Cart after adding item:', cart);
    updateCartDisplay(); // Auto-computes total
    saveCartToStorage();
    showCartNotification('Item added to cart!');
}

function removeFromCart(itemId) {
    cart = cart.filter(item => item.id !== itemId);
    updateCartDisplay();
    saveCartToStorage();
}

function updateItemQuantity(itemId, newQuantity) {
    const item = cart.find(cartItem => cartItem.id === itemId);
    if (item) {
        if (newQuantity <= 0) {
            // Show confirmation dialog before removing item
            if (confirm(`Do you want to remove "${item.name}" from your cart?`)) {
                removeFromCart(itemId);
                showCartNotification(`"${item.name}" removed from cart`);
                
                // If cart becomes empty, show empty state
                if (cart.length === 0) {
                    showCartView();
                }
            } else {
                // User cancelled, revert quantity back to 1
                item.quantity = 1;
                updateCartDisplay();
                saveCartToStorage();
            }
        } else if (newQuantity > 99) {
            // Limit quantity to 99
            item.quantity = 99;
            updateCartDisplay();
            saveCartToStorage();
            // Removed notification for quantity limit
        } else {
            item.quantity = newQuantity;
            updateCartDisplay();
            saveCartToStorage();
        }
    }
}

// Function to update cart item quantity (used by food menu quantity controls)
function updateCartItemQuantity(item, newQuantity) {
    console.log('updateCartItemQuantity called with:', item, 'newQuantity:', newQuantity);
    
    const existingItem = cart.find(cartItem => cartItem.id === item.id);
    
    if (existingItem) {
        // Update existing item quantity
        if (newQuantity < 1) {
            // Don't allow quantities below 1, keep at 1
            existingItem.quantity = 1;
            updateCartDisplay();
            saveCartToStorage();
        } else if (newQuantity > 99) {
            existingItem.quantity = 99;
            updateCartDisplay();
            saveCartToStorage();
        } else {
            existingItem.quantity = newQuantity;
            updateCartDisplay();
            saveCartToStorage();
        }
    } else {
        // Add new item with specified quantity
        if (newQuantity >= 1 && newQuantity <= 99) {
            cart.push({
                ...item,
                quantity: newQuantity
            });
            updateCartDisplay();
            saveCartToStorage();
            showCartNotification('Item added to cart!');
        }
    }
}

function updateCartDisplay() {
    // Update cart count badge in food menu (if it exists)
    updateCartCountBadge();
    
    // Also try to update cart count badge after a short delay to catch any late DOM updates
    setTimeout(() => {
        updateCartCountBadge();
    }, 50);
    
    // Additional update after longer delay to ensure all DOM elements are ready
    setTimeout(() => {
        updateCartCountBadge();
    }, 200);
    
    // Update food menu quantity displays
    updateFoodMenuQuantityDisplays();
    
    // Update cart total
    cartTotal = cart.reduce((sum, item) => sum + (parseFloat(item.price) * item.quantity), 0);
    
    // Debug logging
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    console.log('Cart updated:', {
        items: cart.map(item => ({ name: item.name, quantity: item.quantity, price: item.price, total: parseFloat(item.price) * item.quantity })),
        cartTotal: cartTotal,
        totalItems: totalItems
    });
    
    // Update cart total display if cart view is open
    updateCartTotalDisplay();
    
    // Save to storage immediately
    saveCartToStorage();
}

function updateCartCountBadge() {
    const totalItems = cart.length; // Changed from cart.reduce((sum, item) => sum + item.quantity, 0)
    
    console.log('updateCartCountBadge called with cart:', cart, 'totalItems (number of unique items):', totalItems);
    
    // Try multiple methods to find and update the cart count badge
    let cartItemCount = document.getElementById('cartItemCount');
    
    if (cartItemCount) {
        cartItemCount.textContent = totalItems;
        cartItemCount.style.display = totalItems > 0 ? 'flex' : 'none';
        console.log('✅ Updated cart count badge by ID:', totalItems);
    } else {
        console.log('❌ Cart count badge not found by ID, trying alternative methods...');
        
        // Try to find by other selectors
        const cartButtons = document.querySelectorAll('#viewCartBtn, [id*="viewCartBtn"]');
        console.log('Found cart buttons:', cartButtons.length);
        
        cartButtons.forEach((button, index) => {
            const badge = button.querySelector('span[id*="cartItemCount"], span[style*="position:absolute"]');
            if (badge) {
                badge.textContent = totalItems;
                badge.style.display = totalItems > 0 ? 'flex' : 'none';
                console.log(`✅ Updated cart count badge in button ${index}:`, totalItems);
            } else {
                console.log(`❌ No badge found in button ${index}`);
            }
        });
        
        // Also try to find any span with cart count styling
        const allCartCounts = document.querySelectorAll('span[style*="position:absolute"][style*="background:#ff4757"]');
        console.log('Found cart count badges by styling:', allCartCounts.length);
        
        allCartCounts.forEach((element, index) => {
            element.textContent = totalItems;
            element.style.display = totalItems > 0 ? 'flex' : 'none';
            console.log(`✅ Updated cart count badge ${index} by styling:`, totalItems);
        });
    }
    
    console.log('🎯 Cart count badge update completed. Total items (unique):', totalItems);
}

function updateCartTotalDisplay() {
    // Calculate total cart items and price (all items in cart)
    const totalCartItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    const totalCartPrice = cart.reduce((sum, item) => sum + (parseFloat(item.price) * item.quantity), 0);
    
    // Calculate selected items totals
    const selectedItems = getSelectedCartItems();
    const selectedItemsCount = selectedItems.reduce((sum, item) => sum + item.quantity, 0);
    const selectedItemsPrice = selectedItems.reduce((sum, item) => sum + (parseFloat(item.price) * item.quantity), 0);
    
    console.log('updateCartTotalDisplay called:', {
        totalCartItems: totalCartItems,
        totalCartPrice: totalCartPrice,
        selectedItemsCount: selectedItemsCount,
        selectedItemsPrice: selectedItemsPrice,
        selectedItems: selectedItems.map(item => ({ name: item.name, quantity: item.quantity, price: item.price }))
    });
    
    // Update checkout button to show selected items total
    const checkoutBtn = document.getElementById('checkoutBtn');
    if (checkoutBtn) {
        checkoutBtn.innerHTML = `<i class="fas fa-shopping-cart"></i> Checkout (₱${selectedItemsPrice.toFixed(2)})`;
        // Add a subtle animation to show the total was updated
        checkoutBtn.style.transform = 'scale(1.05)';
        setTimeout(() => {
            checkoutBtn.style.transform = 'scale(1)';
        }, 200);
    }
    
    // Update total items count in cart summary (shows total cart items)
    const totalItemsElement = document.querySelector('.cart-summary .text-right div:first-child');
    if (totalItemsElement) {
        totalItemsElement.textContent = `Total Items: ${totalCartItems}`;
    }
    
    // Add selected items info below the main totals
    updateSelectedItemsDisplay(selectedItemsCount, selectedItemsPrice);
    
    // Update total price in cart summary (shows selected items total)
    const totalPriceElement = document.getElementById('totalPriceDisplay');
    const totalPriceLabel = document.getElementById('totalPriceLabel');
    
    if (totalPriceElement && totalPriceLabel) {
        // Show selected items total, or 0 if no items selected
        const displayPrice = selectedItemsCount > 0 ? selectedItemsPrice : 0;
        const displayLabel = selectedItemsCount > 0 ? 'Selected Total' : 'Total Price';
        
        totalPriceElement.textContent = `₱${displayPrice.toFixed(2)}`;
        totalPriceLabel.textContent = displayLabel;
        
        console.log('Updated total price display:', {
            selectedItemsCount,
            selectedItemsPrice,
            totalCartPrice,
            displayPrice,
            displayLabel
        });
    }
    
    // Update "Select All" checkbox state
    updateSelectAllCheckbox();
}

function updateSelectedItemsDisplay(selectedItemsCount, selectedItemsPrice) {
    // Use the specific ID for the selected items info element
    let selectedInfoElement = document.getElementById('selectedItemsInfo');
    
    // Fallback methods if ID method fails
    if (!selectedInfoElement) {
        // Method 1: Try nth-child selector
        selectedInfoElement = document.querySelector('.cart-summary .text-right div:nth-child(2)');
        
        // Method 2: Try finding by style attribute
        if (!selectedInfoElement) {
            selectedInfoElement = document.querySelector('.cart-summary .text-right div[style*="font-size:12px"]');
        }
        
        // Method 3: Try finding by text content pattern
        if (!selectedInfoElement) {
            const allDivs = document.querySelectorAll('.cart-summary .text-right div');
            selectedInfoElement = Array.from(allDivs).find(div => 
                div.textContent.includes('Selected:') || 
                div.textContent.includes('items (₱')
            );
        }
    }
    
    console.log('updateSelectedItemsDisplay called:', {
        selectedItemsCount,
        selectedItemsPrice,
        selectedInfoElement: !!selectedInfoElement,
        element: selectedInfoElement,
        method: selectedInfoElement ? (selectedInfoElement.id ? 'ID' : 'Selector') : 'Not found'
    });
    
    if (selectedInfoElement) {
        selectedInfoElement.innerHTML = `Selected: ${selectedItemsCount} items (₱${selectedItemsPrice.toFixed(2)})`;
        console.log('Successfully updated selected items display');
    } else {
        console.error('Could not find selected items display element!');
        // Log all available divs for debugging
        const allDivs = document.querySelectorAll('.cart-summary .text-right div');
        console.log('Available divs in text-right:', allDivs.length);
        allDivs.forEach((div, index) => {
            console.log(`Div ${index}:`, div.textContent, div.outerHTML);
        });
    }
}

function getSelectedCartItems() {
    const selectedItems = [];
    const checkboxes = document.querySelectorAll('.cart-item-checkbox');
    
    console.log('getSelectedCartItems called, found checkboxes:', checkboxes.length);
    
    checkboxes.forEach((checkbox) => {
        if (checkbox.checked) {
            // Find the cart item by matching the item ID from the checkbox's parent cart item
            const cartItemElement = checkbox.closest('.cart-item');
            if (cartItemElement) {
                const itemId = cartItemElement.getAttribute('data-item-id');
                const cartItem = cart.find(item => item.id === itemId);
                if (cartItem) {
                    selectedItems.push(cartItem);
                    console.log('Selected item:', cartItem.name, 'quantity:', cartItem.quantity, 'price:', cartItem.price);
                }
            }
        }
    });
    
    console.log('Total selected items:', selectedItems.length);
    return selectedItems;
}

function updateSelectAllCheckbox() {
    const selectAllCheckbox = document.getElementById('selectAllCheckbox');
    const itemCheckboxes = document.querySelectorAll('.cart-item-checkbox');
    
    console.log('updateSelectAllCheckbox called:', {
        selectAllCheckbox: !!selectAllCheckbox,
        itemCheckboxesCount: itemCheckboxes.length
    });
    
    if (selectAllCheckbox && itemCheckboxes.length > 0) {
        const checkedCount = Array.from(itemCheckboxes).filter(cb => cb.checked).length;
        const totalCount = itemCheckboxes.length;
        
        console.log('Checkbox states:', { checkedCount, totalCount });
        
        // Update select all checkbox state
        selectAllCheckbox.checked = checkedCount === totalCount;
        selectAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < totalCount;
        
        console.log('Select all checkbox updated:', {
            checked: selectAllCheckbox.checked,
            indeterminate: selectAllCheckbox.indeterminate
        });
        
        // Update visual appearance of cart items based on checkbox state
        updateCartItemVisualStates();
    }
}

function updateCartItemVisualStates() {
    const cartItems = document.querySelectorAll('.cart-item');
    cartItems.forEach(cartItem => {
        const checkbox = cartItem.querySelector('.cart-item-checkbox');
        if (checkbox) {
            if (checkbox.checked) {
                // Selected state - normal appearance
                cartItem.style.background = '#fff';
                cartItem.style.opacity = '1';
                cartItem.style.filter = 'none';
            } else {
                // Unselected state - dimmed appearance
                cartItem.style.background = '#f8f9fa';
                cartItem.style.opacity = '0.7';
                cartItem.style.filter = 'grayscale(20%)';
            }
        }
    });
}

function saveCartToStorage() {
    localStorage.setItem('foodCart', JSON.stringify(cart));
}

function refreshCartView() {
    // Only refresh if cart view is currently open
    const foodMenuContent = document.getElementById('food-menu-content');
    if (foodMenuContent && foodMenuContent.innerHTML.includes('cart-view')) {
        showCartView();
        // Ensure totals are updated after refresh
        setTimeout(() => {
            updateCartTotalDisplay();
        }, 200);
    }
}

function loadCartFromStorage() {
    const savedCart = localStorage.getItem('foodCart');
    if (savedCart) {
        try {
        cart = JSON.parse(savedCart);
            console.log('Cart loaded from storage:', cart);
        updateCartDisplay();
        } catch (error) {
            console.error('Error parsing cart from storage:', error);
            cart = [];
            localStorage.removeItem('foodCart');
        }
    } else {
        console.log('No cart data found in storage');
        cart = [];
    }
}

function clearCart() {
    if (cart.length === 0) {
        showCartNotification('Your cart is already empty');
        return;
    }
    
    // Show confirmation dialog
    const confirmed = confirm(`Do you want to clear your cart?\n\nThis will remove ${cart.length} item(s) from your cart.\n\nThis action cannot be undone.`);
    
    if (confirmed) {
        const itemCount = cart.length;
    cart = [];
    updateCartDisplay();
    saveCartToStorage();
        showCartNotification(`Cart cleared! Removed ${itemCount} item(s)`);
        
        // If we're in cart view, refresh it to show empty state
        const foodMenuContent = document.getElementById('food-menu-content');
        if (foodMenuContent && foodMenuContent.innerHTML.includes('cart-view')) {
            showCartView();
        }
    }
}

function showCartNotification(message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #8b5e3b;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 9999;
        font-weight: 600;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

function showCartView() {
    const foodMenuContent = document.getElementById('food-menu-content');
    if (!foodMenuContent) return;
    
    if (cart.length === 0) {
        const emptyCartHtml = `
            <div class="cart-empty" style="text-align:center;padding:60px 20px;">
                <i class="fas fa-shopping-cart" style="font-size:4rem;color:#ccc;margin-bottom:20px;"></i>
                <h3 style="color:#666;margin-bottom:10px;">Your cart is empty</h3>
                <p style="color:#999;margin-bottom:30px;">Add some delicious items to get started!</p>
                <button class="btn btn-primary" onclick="showFoodMenuModal()" style="background:#8b5e3b;border:none;padding:6px 12px;border-radius:4px;font-size:12px;font-weight:600;color:white;box-shadow:0 1px 4px rgba(139,94,59,0.2);transition:all 0.2s ease;cursor:pointer;">
                    <i class="fas fa-utensils" style="margin-right:4px;"></i> Browse Menu
                </button>
            </div>
        `;
        foodMenuContent.innerHTML = `<div class='food-menu-content-card'>${emptyCartHtml}</div>`;
        
        // Add hover effects for the browse menu button
        const browseMenuBtn = document.querySelector('.btn-primary');
        if (browseMenuBtn) {
            browseMenuBtn.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-1px)';
                this.style.boxShadow = '0 4px 12px rgba(139,94,59,0.3)';
                this.style.background = '#a67c52';
            });
            
            browseMenuBtn.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = '0 2px 8px rgba(139,94,59,0.2)';
                this.style.background = '#8b5e3b';
            });
            
            browseMenuBtn.addEventListener('mousedown', function() {
                this.style.transform = 'translateY(0px) scale(0.98)';
            });
            
            browseMenuBtn.addEventListener('mouseup', function() {
                this.style.transform = 'translateY(-1px) scale(1)';
            });
        }
        
        return;
    }
    
    let cartHtml = `
        <div class="cart-view" style="max-width:1200px;margin:0 auto;">
            <div style="display:flex;align-items:center;margin-bottom:20px;">
                <button type="button" id="backToMenuBtn" style="background:none;border:none;font-size:1.8rem;color:#6D4C41;margin-right:12px;cursor:pointer;line-height:1;" aria-label="Back">&#8592;</button>
                <h3 style='font-weight:700;margin:0;'>Shopping Cart (${cart.length} items)</h3>
            </div>
            
            <div class="cart-items" style="margin-bottom:20px;">
    `;
    
    cart.forEach(item => {
        const itemTotal = (parseFloat(item.price) * item.quantity).toFixed(2);
        cartHtml += `
            <div class="cart-item" data-item-id="${item.id}" style="background:#fff;border-radius:12px;padding:16px;margin-bottom:12px;box-shadow:0 2px 8px rgba(0,0,0,0.1);display:flex;align-items:center;gap:16px;transition:all 0.3s ease;">
                <input type="checkbox" class="cart-item-checkbox" checked style="width:20px;height:20px;accent-color:#8b5e3b;">
                
                <img src="${item.image}" alt="${item.name}" style="width:80px;height:80px;object-fit:cover;border-radius:8px;">
                
                <div class="cart-item-details" style="flex:1;">
                    <h4 style="margin:0 0 4px 0;color:#4e342e;font-size:16px;">${item.name}</h4>
                    <p style="margin:0 0 8px 0;color:#666;font-size:14px;">${item.description || ''}</p>
                    <div style="color:#8b5e3b;font-weight:600;font-size:18px;">₱${item.price}</div>
                </div>
                
                <div class="cart-item-quantity" style="display:flex;align-items:center;gap:8px;">
                    <button class="quantity-btn minus-btn" data-item-id="${item.id}" style="background:#f8f9fa;border:1px solid #dee2e6;border-radius:50%;width:32px;height:32px;display:flex;align-items:center;justify-content:center;cursor:pointer;font-weight:bold;color:#6D4C41;">-</button>
                    <span class="quantity-display" style="min-width:40px;text-align:center;font-weight:600;font-size:16px;">${item.quantity}</span>
                    <button class="quantity-btn plus-btn ${item.quantity >= 99 ? 'disabled' : ''}" data-item-id="${item.id}" style="background:#f8f9fa;border:1px solid #dee2e6;border-radius:50%;width:32px;height:32px;display:flex;align-items:center;justify-content:center;cursor:pointer;font-weight:bold;color:#6D4C41;" ${item.quantity >= 99 ? 'disabled' : ''}>+</button>
                </div>
                
                <div class="cart-item-total" style="text-align:right;min-width:80px;">
                    <div style="font-weight:600;font-size:16px;color:#8b5e3b;">₱${itemTotal}</div>
                </div>
                
                <button class="remove-item-btn" data-item-id="${item.id}" style="background:none;border:none;color:#dc3545;cursor:pointer;font-size:18px;padding:4px;" title="Remove item">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
    });
    
    cartHtml += `
            </div>
            
            <div class="cart-summary" style="background:#f8f9fa;border-radius:12px;padding:20px;margin-bottom:20px;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
                    <div style="display:flex;align-items:center;gap:8px;">
                        <input type="checkbox" id="selectAllCheckbox" checked style="width:20px;height:20px;accent-color:#8b5e3b;">
                        <label for="selectAllCheckbox" style="font-weight:600;color:#4e342e;">Select All</label>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:14px;color:#666;">Total Items: ${cart.reduce((sum, item) => sum + item.quantity, 0)}</div>
                        <div id="selectedItemsInfo" style="font-size:12px;color:#999;margin:4px 0;">Selected: 0 items (₱0.00)</div>
                        <div id="totalPriceLabel" style="font-size:12px;color:#666;margin-bottom:4px;">Total Price</div>
                        <div id="totalPriceDisplay" style="font-size:24px;font-weight:700;color:#8b5e3b;">₱${cartTotal.toFixed(2)}</div>
                    </div>
                </div>
                
                <div style="display:flex;gap:12px;">
                    <button class="btn btn-secondary" onclick="clearCart()" style="flex:1;background:#6c757d;border:none;padding:12px;border-radius:8px;color:white;font-weight:600;" title="Clear all items from cart">
                        <i class="fas fa-trash-alt"></i> Clear Cart
                    </button>
                    <button class="btn btn-primary" id="checkoutBtn" style="flex:2;background:#8b5e3b;border:none;padding:12px;border-radius:8px;color:white;font-weight:600;">
                        <i class="fas fa-shopping-cart"></i> Checkout Selected Items
                    </button>
                </div>
            </div>
        </div>
    `;
    
    foodMenuContent.innerHTML = `<div class='food-menu-content-card'>${cartHtml}</div>`;
    
    // Add event listeners for cart functionality
    addCartEventListeners();
    
    // Update totals immediately after rendering
    updateCartTotalDisplay();
    
    // Ensure cart total is properly calculated and displayed AFTER event listeners are added
    setTimeout(() => {
        updateCartDisplay();
        updateCartTotalDisplay(); // This will show the selected items info
        updateCartItemVisualStates(); // Update visual states of cart items
        console.log('Cart view initialized with auto-computation enabled');
    }, 100);
}

function addCartEventListeners() {
    // Quantity buttons
    document.querySelectorAll('.quantity-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const itemId = this.getAttribute('data-item-id');
            const isPlus = this.classList.contains('plus-btn');
            const item = cart.find(cartItem => cartItem.id === itemId);
            
            if (item) {
                let newQuantity;
                if (isPlus) {
                    if (item.quantity >= 99) {
                        // Removed notification for quantity limit
                        return;
                    }
                    newQuantity = item.quantity + 1;
                } else {
                    newQuantity = item.quantity - 1;
                }
                
                // Update quantity and handle cart updates
                updateItemQuantity(itemId, newQuantity);
                
                // Refresh cart view efficiently
                refreshCartView();
            }
        });
    });
    
    // Remove buttons
    document.querySelectorAll('.remove-item-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const itemId = this.getAttribute('data-item-id');
            const item = cart.find(cartItem => cartItem.id === itemId);
            
            if (item && confirm(`Do you want to remove "${item.name}" from your cart?`)) {
                removeFromCart(itemId);
                showCartNotification(`"${item.name}" removed from cart`);
                
                // Refresh cart view efficiently
                refreshCartView();
            }
        });
    });
    
    // Select all checkbox - selects all items when clicked
    const selectAllCheckbox = document.getElementById('selectAllCheckbox');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            console.log('Select all checkbox changed:', this.checked);
            const checkboxes = document.querySelectorAll('.cart-item-checkbox');
            checkboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            // Auto-compute totals when select all changes
            updateCartTotalDisplay();
            // Update select all checkbox state
            updateSelectAllCheckbox();
        });
    }
    
    // Individual item checkboxes
    document.querySelectorAll('.cart-item-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            console.log('Individual checkbox changed:', this.checked, 'for item:', this.closest('.cart-item')?.getAttribute('data-item-id'));
            // Auto-compute totals when individual items are selected/deselected
            updateCartTotalDisplay();
            // Update select all checkbox state
            updateSelectAllCheckbox();
        });
    });
    
    // Back to menu button
    const backToMenuBtn = document.getElementById('backToMenuBtn');
    if (backToMenuBtn) {
        backToMenuBtn.addEventListener('click', function() {
            showFoodMenuModal();
        });
    }
    
    // Checkout button
    const checkoutBtn = document.getElementById('checkoutBtn');
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', function() {
            // Get selected items based on checkbox selections
            const selectedItems = getSelectedCartItems();
            
            if (selectedItems.length === 0) {
                alert('Please select at least one item to checkout.');
                return;
            }
            
            console.log('Checkout clicked - cart items:', cart);
            console.log('Selected items for checkout:', selectedItems);
            
            // Proceed to checkout with selected items only
            proceedToCheckout(selectedItems);
        });
    }
}

function proceedToCheckout(selectedItems) {
    console.log('=== PROCEED TO CHECKOUT ===');
    console.log('selectedItems received:', selectedItems);
    console.log('selectedItems length:', selectedItems.length);
    console.log('selectedItems content:', JSON.stringify(selectedItems, null, 2));
    
    // Get user info from hidden fields
    const userId = document.getElementById('user-id')?.value || '';
    const userName = document.getElementById('user-name')?.value || 'Guest User';
    const userPhone = document.getElementById('user-phone')?.value || '+639000000000';
    const userAddress = document.getElementById('user-address')?.value || 'Santa Cruz, Laguna';
    const userEmail = document.getElementById('user-email')?.value || 'guest@example.com';
    
    // Calculate totals for selected items
    const subtotal = selectedItems.reduce((sum, item) => sum + (parseFloat(item.price) * item.quantity), 0);
    const deliveryFee = 50;
    const totalAmount = subtotal + deliveryFee;
    
    // Build checkout form HTML
    const checkoutHtml = `
        <form id="cartCheckoutForm" autocomplete="off" style="max-width:1200px;width:100%;margin:0;padding:12px 32px;border-radius:24px;background:#f8f9fa;box-shadow:0 4px 24px rgba(0,0,0,0.08);font-size:1.15rem;">
            <div style="display:flex;align-items:center;margin-bottom:18px;">
                <button type="button" id="backFromCheckoutBtn" style="background:none;border:none;font-size:1.8rem;color:#6D4C41;margin-right:12px;cursor:pointer;line-height:1;" aria-label="Back">&#8592;</button>
                <h3 style='font-weight:700;margin:0;'>Checkout</h3>
            </div>

            <!-- Room Selection Section -->
            <div class="mb-4" style="background:#fff;padding:16px;border-radius:12px;border:2px solid #6D4C41;">
                <h5 style='margin-top:0;margin-bottom:12px;color:#6D4C41;'>Room Selection <span style="color:red">*</span></h5>
                <div class="mb-2">
                    <label for="checkoutRoomSelect" class="form-label">Select Room for Delivery</label>
                    <select id="checkoutRoomSelect" class="form-select" required>
                        <option value="" disabled selected>Select a room</option>
                        ${getApprovedBookingsOptions()}
                    </select>
                    <div class="invalid-feedback">Please select a room for delivery.</div>
                </div>
                <div class="mb-2">
                    <label for="checkoutDeliveryNotes" class="form-label">Delivery Notes</label>
                    <textarea id="checkoutDeliveryNotes" class="form-control" placeholder="Room info will appear here" aria-label="Delivery Notes" readonly></textarea>
                </div>
            </div>

            <!-- Ordered Item Section -->
            <div class="mb-4" style="background:#fff;padding:16px;border-radius:12px;border:2px solid #6D4C41;">
                <h5 style='margin-top:0;margin-bottom:12px;color:#6D4C41;'>Ordered Item</h5>
                ${selectedItems.map(item => `
                    <div style="display:flex;align-items:center;gap:16px;">
                        <img src="${item.image}" alt="${item.name}" style="width:60px;height:60px;object-fit:cover;border-radius:8px;">
                        <div>
                            <div style="font-weight:600;font-size:1.1rem;">${item.name}</div>
                            <div style="color:#555;font-size:0.98rem;margin-bottom:2px;">${item.description || ''}</div>
                            <div style="color:#6D4C41;font-weight:500;">₱${item.price}</div>
                        </div>
                    </div>
                `).join('')}
            </div>

            <!-- Contact Information -->
            <h5 style='margin-top:24px;margin-bottom:10px;'>Contact Information <span style="font-size:0.9em;color:#6c757d;font-weight:normal;">(Auto-filled from your profile)</span></h5>
            <div class="mb-2">
                <label for="checkoutFullName" class="form-label">Full Name</label>
                <div class="input-group">
                    <input type="text" id="checkoutFullName" class="form-control" value="${userName}" readonly style="background-color:#f8f9fa;border-color:#dee2e6;">
                    <span class="input-group-text" style="background-color:#e7d7ce;border-color:#dee2e6;color:#6D4C41;">
                        <i class="fas fa-user-check"></i>
                    </span>
                </div>
            </div>
            <div class="mb-2">
                <label for="checkoutEmail" class="form-label">Email</label>
                <div class="input-group">
                    <input type="email" id="checkoutEmail" class="form-control" value="${userEmail}" readonly style="background-color:#f8f9fa;border-color:#dee2e6;">
                    <span class="input-group-text" style="background-color:#e7d7ce;border-color:#dee2e6;color:#6D4C41;">
                        <i class="fas fa-envelope"></i>
                    </span>
                </div>
            </div>
            <div class="mb-2">
                <label for="checkoutPhone" class="form-label">Phone Number</label>
                <div class="input-group">
                    <input type="tel" id="checkoutPhone" class="form-control" value="${userPhone}" readonly style="background-color:#f8f9fa;border-color:#dee2e6;">
                    <span class="input-group-text" style="background-color:#e7d7ce;border-color:#dee2e6;color:#6D4C41;">
                        <i class="fas fa-phone"></i>
                    </span>
                </div>
            </div>

            <!-- Payment Method Section -->
            <div class="mb-4" style="background:#fff;padding:16px;border-radius:12px;border:2px solid #6D4C41;">
                <h5 style='margin-top:0;margin-bottom:12px;color:#6D4C41;'>Payment Method <span style="color:red">*</span></h5>
                <div class="mb-2">
                    <select id="checkoutPaymentMethodSelect" class="form-select" required aria-label="Payment Method">
                        <option value="" disabled selected>Select payment method</option>
                        <option value="cod">Cash on Delivery</option>
                        <option value="gcash">GCash</option>
                        <option value="half_payment">Half Payment (GCash + COD)</option>
                    </select>
                    <div class="invalid-feedback">Please select a payment method.</div>
                </div>
                <div id="checkoutGcashQrSection" style="display:none;text-align:left;margin-top:12px;">
                    <button type="button" id="checkoutShowGcashQrBtn" class="btn" style="background:rgba(109,76,65,0.08);color:#6D4C41;font-weight:600;border-radius:2rem;padding:0.55em 2.2em;display:inline-flex;align-items:center;gap:0.9em;border:2px solid #6D4C41;">
                        <i class="fas fa-qrcode" aria-hidden="true" style="font-size:1.2em;"></i> Show Electronic Payment
                    </button>
                </div>
            </div>

            <h5 style='margin-top:24px;margin-bottom:10px;'>Delivery Address</h5>
            <div class="mb-2">
                <label for="checkoutBarangay" class="form-label">Barangay</label>
                <select id="checkoutBarangay" class="form-select" required aria-label="Barangay" readonly>
                    <option value="Santa Cruz" selected>Santa Cruz</option>
                </select>
            </div>
            <div class="mb-2">
                <label for="checkoutSitio" class="form-label">Sitio/Purok</label>
                <select id="checkoutSitio" class="form-select" required aria-label="Sitio/Purok" readonly>
                    <option value="Central" selected>Central</option>
                </select>
            </div>
            <div class="mb-2">
                <label for="checkoutLandmarks" class="form-label">Landmarks</label>
                <input type="text" id="checkoutLandmarks" class="form-control" placeholder="Nearby landmarks or additional directions" aria-label="Landmarks" value="Fawna Hotel" readonly>
            </div>

            <!-- Order Summary -->
            <div class="mb-4" style="background:#fff;padding:16px;border-radius:12px;margin-top:24px;">
                <h5 style='margin-top:0;margin-bottom:12px;'>Order Summary</h5>
                ${selectedItems.map(item => `
                    <div style="border:1px solid #e0e0e0;border-radius:8px;padding:12px 16px;margin-bottom:16px;display:flex;align-items:center;gap:16px;">
                        <img src="${item.image}" alt="${item.name}" style="width:60px;height:60px;object-fit:cover;border-radius:8px;">
                        <div style="flex:1;">
                            <div style="font-weight:600;font-size:1.1rem;">${item.name}</div>
                            <div style="color:#555;font-size:0.98rem;margin-bottom:2px;">${item.description || ''}</div>
                            <div style="color:#6D4C41;font-weight:500;">₱${item.price} × ${item.quantity}</div>
                        </div>
                        <div style="color:#8b5e3b;font-weight:600;font-size:1.1rem;">₱${(parseFloat(item.price) * item.quantity).toFixed(2)}</div>
                    </div>
                `).join('')}
                
                <div id="orderBreakdown" style="font-size:1.08em;color:#4e342e;">
                    <div style="display:flex;justify-content:space-between;"><span>Subtotal:</span><span>₱${subtotal.toFixed(2)}</span></div>
                    <div style="display:flex;justify-content:space-between;"><span>Delivery Fee:</span><span>₱${deliveryFee.toFixed(2)}</span></div>
                    <div style="display:flex;justify-content:space-between;font-weight:700;border-top:1px solid #e0e0e0;margin-top:8px;padding-top:8px;"><span>Total:</span><span>₱${totalAmount.toFixed(2)}</span></div>
                </div>
            </div>

            <div class="mt-4" style="text-align:center;">
                <button type="submit" class="btn btn-lg btn-primary" id="confirmCartOrderBtn" style="min-width:160px;margin-right:12px;background:#8b5e3b;border:none;">
                    <span id="confirmCartOrderBtnText">Confirm Order</span>
                    <span id="confirmCartOrderSpinner" class="spinner-border spinner-border-sm" style="display:none;" role="status" aria-hidden="true"></span>
                </button>
                <button type="button" class="btn btn-lg btn-secondary" id="cancelCartOrderBtn" style="min-width:120px;">Cancel</button>
            </div>
        </form>
    `;
    
    const foodMenuContent = document.getElementById('food-menu-content');
    if (foodMenuContent) {
        foodMenuContent.innerHTML = `<div class='food-menu-content-card'>${checkoutHtml}</div>`;
        
        // Add event listeners
        const backBtn = document.getElementById('backFromCheckoutBtn');
        if (backBtn) {
            backBtn.addEventListener('click', showCartView);
        }
        
        const cancelBtn = document.getElementById('cancelCartOrderBtn');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', showCartView);
        }
        
        const form = document.getElementById('cartCheckoutForm');
        if (form) {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                submitCartOrder(selectedItems, subtotal, deliveryFee, totalAmount);
            });
        }

        // Add payment method event listeners
        const paymentMethodSelect = document.getElementById('checkoutPaymentMethodSelect');
        if (paymentMethodSelect) {
            paymentMethodSelect.addEventListener('change', function() {
                const gcashQrSection = document.getElementById('checkoutGcashQrSection');
                if (this.value === 'gcash' || this.value === 'half_payment') {
                    gcashQrSection.style.display = 'block';
                } else {
                    gcashQrSection.style.display = 'none';
                }
            });
        }

        const showGcashQrBtn = document.getElementById('checkoutShowGcashQrBtn');
        if (showGcashQrBtn) {
            showGcashQrBtn.addEventListener('click', function() {
                showGcashQrModal();
            });
        }

        // Add room selection event listener for delivery notes
         const roomSelect = document.getElementById('checkoutRoomSelect');
         if (roomSelect) {
             roomSelect.addEventListener('change', function() {
                 const deliveryNotes = document.getElementById('checkoutDeliveryNotes');
                 if (this.value) {
                     const selectedOption = this.options[this.selectedIndex];
                     const roomInfo = selectedOption.textContent;
                     
                     // Create ordered items list
                     const orderedItemsList = selectedItems.map(item => 
                         `${item.name} (${item.quantity}x) - ₱${item.price}`
                     ).join('\n');
                     
                     // Combine room info with ordered items
                     deliveryNotes.value = `${roomInfo}\n\nOrdered Items:\n${orderedItemsList}`;
                     
                     // Expand textarea height based on number of items
                     const itemCount = selectedItems.length;
                     if (itemCount > 3) {
                         deliveryNotes.style.height = `${Math.min(120 + (itemCount - 3) * 20, 200)}px`;
                         deliveryNotes.style.minHeight = '120px';
                     } else {
                         deliveryNotes.style.height = '120px';
                     }
                 } else {
                     deliveryNotes.value = '';
                 }
             });
             
                              // Auto-populate delivery notes with ordered items when modal opens
                 const deliveryNotes = document.getElementById('checkoutDeliveryNotes');
                 if (deliveryNotes && selectedItems && selectedItems.length > 0) {
                     const orderedItemsList = selectedItems.map(item => 
                         `${item.name} (${item.quantity}x) - ₱${item.price}`
                     ).join('\n');
                     
                     deliveryNotes.value = `Ordered Items:\n${orderedItemsList}`;
                     
                     // Expand textarea height based on number of items
                     const itemCount = selectedItems.length;
                     if (itemCount > 3) {
                         deliveryNotes.style.height = `${Math.min(120 + (itemCount - 3) * 20, 200)}px`;
                         deliveryNotes.style.minHeight = '120px';
                     } else {
                         deliveryNotes.style.height = '120px';
                     }
                 }
         }
    }
}

function getApprovedBookingsOptions() {
    let approvedBookings = [];
    const approvedBookingsInput = document.getElementById('approved-bookings-json');
    if (approvedBookingsInput) {
        try {
            approvedBookings = JSON.parse(approvedBookingsInput.value);
        } catch (e) { 
            approvedBookings = []; 
        }
    }
    
    // If no approved bookings in the hidden input, try to fetch them
    if (approvedBookings.length === 0) {
        fetchApprovedBookings();
        return '<option value="">Loading rooms...</option>';
    }
    
    return approvedBookings.map(b => `<option value="${b.id}">Room ${b.room_number} (${b.room_type}) - Booking #${b.id}</option>`).join('');
}

// Function to fetch approved bookings from the server
function fetchApprovedBookings() {
    fetch('/api/user/approved-bookings')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.bookings) {
                // Update the hidden input with the fetched data
                const approvedBookingsInput = document.getElementById('approved-bookings-json');
                if (approvedBookingsInput) {
                    approvedBookingsInput.value = JSON.stringify(data.bookings);
                }
                
                // Update any existing room select dropdowns
                updateRoomSelectDropdowns(data.bookings);
            }
        })
        .catch(error => {
            console.error('Error fetching approved bookings:', error);
        });
}

// Function to update room select dropdowns with approved bookings
function updateRoomSelectDropdowns(bookings) {
    const roomSelects = document.querySelectorAll('#approvedRoomSelect, #checkoutRoomSelect');
    roomSelects.forEach(select => {
        if (select) {
            const currentValue = select.value;
            select.innerHTML = '<option value="">Select Room for Delivery</option>';
            bookings.forEach(booking => {
                const option = document.createElement('option');
                option.value = booking.id;
                option.textContent = `Room ${booking.room_number} (${booking.room_type}) - Booking #${booking.id}`;
                select.appendChild(option);
            });
            select.value = currentValue; // Restore the previous selection
        }
    });
}

function submitCartOrder(selectedItems, subtotal, deliveryFee, totalAmount) {
    const confirmBtn = document.getElementById('confirmCartOrderBtn');
    const confirmText = document.getElementById('confirmCartOrderBtnText');
    const spinner = document.getElementById('confirmCartOrderSpinner');
    
    // Show loading state
    confirmBtn.disabled = true;
    confirmText.style.display = 'none';
    spinner.style.display = 'inline-block';
    
    // Get form data
    const roomId = document.getElementById('checkoutRoomSelect').value;
    const paymentMethod = document.getElementById('checkoutPaymentMethodSelect').value;
    const barangay = document.getElementById('checkoutBarangay').value;
    const sitio = document.getElementById('checkoutSitio').value;
    const landmarks = document.getElementById('checkoutLandmarks').value;
    const deliveryNotes = document.getElementById('checkoutDeliveryNotes').value;
    const userId = document.getElementById('user-id')?.value || '';
    const userName = document.getElementById('user-name')?.value || 'Guest User';
    const userPhone = document.getElementById('user-phone')?.value || '+639000000000';
    const userEmail = document.getElementById('user-email')?.value || 'guest@example.com';
    
    // Validate required fields
    if (!roomId) {
        alert('Please select a room for delivery.');
        return;
    }
    if (!paymentMethod) {
        alert('Please select a payment method.');
        return;
    }
    
    // Prepare order data
    const orderData = {
        user_id: userId,
        full_name: userName,
        phone: userPhone,
        email: userEmail,
        delivery_address: `Room ${roomId}, ${sitio}, ${barangay}, ${landmarks}`,
        payment_method: paymentMethod,
        notes: '',
        delivery_notes: deliveryNotes,
        subtotal: subtotal,
        delivery_fee: deliveryFee,
        total_amount: totalAmount,
        items: selectedItems.map(item => ({
            menu_item_id: item.id,
            name: item.name,
            price: item.price,
            quantity: item.quantity,
            image: item.image,
            description: item.description
        }))
    };
    
    // Submit order
    console.log('Submitting order with data:', orderData);
    
    fetch('/api/order-food', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
        },
        body: JSON.stringify(orderData)
    })
    .then(response => {
        console.log('Order response status:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Order response data:', data);
        if (data.success) {
            // Remove ordered items from cart
            selectedItems.forEach(item => {
                removeFromCart(item.id);
            });
            
            // Hide checkout modal
            const checkoutModal = document.getElementById('checkoutModal');
            if (checkoutModal && typeof bootstrap !== 'undefined') {
                const modalInstance = bootstrap.Modal.getInstance(checkoutModal);
                if (modalInstance) modalInstance.hide();
            }
            
            // Show proper success message
            showOrderSuccessMessage('Order placed successfully! Your food will be delivered to your room shortly.');
            
            // Return to menu after a short delay
            setTimeout(() => {
                showFoodMenuModal();
            }, 2000);
        } else {
            showOrderErrorMessage('Error placing order: ' + (data.message || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error placing order:', error);
        showOrderErrorMessage('Error placing order. Please try again.');
    })
    .finally(() => {
        // Reset button state
        confirmBtn.disabled = false;
        confirmText.style.display = 'inline';
        spinner.style.display = 'none';
    });
}

// Helper function to show order success message
function showOrderSuccessMessage(message) {
    // Create or get success modal
    let successModal = document.getElementById('orderSuccessDialog');
    if (!successModal) {
        successModal = createSuccessModal();
    }
    
    // Update modal content
    const modalBody = successModal.querySelector('.modal-body');
    modalBody.innerHTML = `
        <div class="text-center">
            <div class="mb-3">
                <i class="fas fa-check-circle" style="font-size: 3rem; color: #8b5e3b;"></i>
            </div>
            <h5 class="mb-3" style="color: #8b5e3b;">Order Confirmed!</h5>
            <p class="mb-0">${message}</p>
        </div>
    `;
    
    // Show the modal
    if (typeof bootstrap !== 'undefined') {
        const modal = new bootstrap.Modal(successModal, {
            backdrop: 'static',
            keyboard: false
        });
        modal.show();
    }
}

// Helper function to show order error message
function showOrderErrorMessage(message) {
    // Create or get error modal
    let errorModal = document.getElementById('orderErrorDialog');
    if (!errorModal) {
        errorModal = createErrorModal();
    }
    
    // Update modal content
    const modalBody = errorModal.querySelector('.modal-body');
    modalBody.innerHTML = `
        <div class="text-center">
            <div class="mb-3">
                <i class="fas fa-exclamation-triangle" style="font-size: 3rem; color: #dc3545;"></i>
            </div>
            <h5 class="mb-3" style="color: #dc3545;">Order Failed</h5>
            <p class="mb-0">${message}</p>
        </div>
    `;
    
    // Show the modal
    if (typeof bootstrap !== 'undefined') {
        const modal = new bootstrap.Modal(errorModal, {
            backdrop: 'static',
            keyboard: false
        });
        modal.show();
    }
}

// Helper function to create success modal
function createSuccessModal() {
    const modalHtml = `
        <div class="modal fade" id="orderSuccessDialog" tabindex="-1" aria-labelledby="orderSuccessDialogLabel" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header border-0 pb-0">
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body text-center px-4 pb-4">
                        <!-- Content will be dynamically inserted -->
                    </div>
                    <div class="modal-footer border-0 pt-0 justify-content-center">
                        <button type="button" class="btn px-4" data-bs-dismiss="modal" style="background-color: #8b5e3b; border-color: #8b5e3b; color: white;">OK</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    return document.getElementById('orderSuccessDialog');
}

// Helper function to create error modal
function createErrorModal() {
    const modalHtml = `
        <div class="modal fade" id="orderErrorDialog" tabindex="-1" aria-labelledby="orderErrorDialogLabel" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header border-0 pb-0">
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body text-center px-4 pb-4">
                        <!-- Content will be dynamically inserted -->
                    </div>
                    <div class="modal-footer border-0 pt-0 justify-content-center">
                        <button type="button" class="btn px-4" data-bs-dismiss="modal" style="background-color: #dc3545; border-color: #dc3545; color: white;">OK</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    return document.getElementById('orderErrorDialog');
}

// Load cart from storage when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, loading cart from storage...');
    loadCartFromStorage();
    
    // Initialize food menu modal transition properties
    setTimeout(() => {
        const foodMenuModal = document.getElementById('foodMenuModal');
        if (foodMenuModal) {
            console.log('Initializing food menu modal transition properties...');
            foodMenuModal.style.transition = 'opacity 0.3s ease-in-out, visibility 0.3s ease-in-out';
            foodMenuModal.style.opacity = '1';
            foodMenuModal.style.visibility = 'visible';
        }
    }, 100);
    
    // Debug cart state
    setTimeout(() => {
        debugCart();
    }, 200);
    
    // Update cart count badge after a short delay to ensure all elements are ready
    setTimeout(() => {
        console.log('Updating cart count badge after DOM load...');
        updateCartCountBadge();
    }, 100);
    
    // Also update after a longer delay to catch any late-loading elements
    setTimeout(() => {
        console.log('Final cart count badge update after DOM load...');
        updateCartCountBadge();
    }, 500);
});

// Add event listeners for cart functionality
document.addEventListener('click', function(e) {
    // Add to cart button (legacy - now replaced by quantity controls)
    if (e.target.classList.contains('cart-add-btn')) {
        const item = {
            id: e.target.getAttribute('data-id'),
            name: e.target.getAttribute('data-name'),
            price: parseFloat(e.target.getAttribute('data-price')), // Ensure price is a number
            image: e.target.getAttribute('data-image'),
            description: e.target.getAttribute('data-description')
        };
        console.log('Adding item to cart:', item);
        addToCart(item);
    }
    
    // View cart button
    if (e.target.closest('#viewCartBtn')) {
        showCartView();
  }
});

// Function to add event listeners for food menu quantity controls
function addFoodMenuQuantityEventListeners() {
    // Plus button
    document.querySelectorAll('.quantity-btn.plus-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const itemId = this.getAttribute('data-id');
            const quantityDisplay = this.parentElement.querySelector('.quantity-display');
            const currentQuantity = parseInt(quantityDisplay.textContent) || 0;
            const newQuantity = currentQuantity + 1;
            
            // Just update the display quantity (preview)
            quantityDisplay.textContent = newQuantity;
            
            // Update button states
            const minusBtn = this.parentElement.querySelector('.minus-btn');
            if (minusBtn) {
                minusBtn.style.opacity = newQuantity > 0 ? '1' : '0.5';
                minusBtn.style.cursor = newQuantity > 0 ? 'pointer' : 'not-allowed';
            }
        });
    });
    
    // Minus button
    document.querySelectorAll('.quantity-btn.minus-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const itemId = this.getAttribute('data-id');
            const quantityDisplay = this.parentElement.querySelector('.quantity-display');
            const currentQuantity = parseInt(quantityDisplay.textContent) || 1;
            const newQuantity = Math.max(1, currentQuantity - 1);
            
            // Just update the display quantity (preview)
            quantityDisplay.textContent = newQuantity;
            
            // Update button states
            const minusBtn = this.parentElement.querySelector('.minus-btn');
            if (minusBtn) {
                minusBtn.style.opacity = newQuantity > 1 ? '1' : '0.5';
                minusBtn.style.cursor = newQuantity > 1 ? 'pointer' : 'not-allowed';
            }
        });
    });
    
    // Add to Cart button
    document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const itemId = this.getAttribute('data-id');
            const quantityDisplay = this.closest('.food-menu-item').querySelector('.quantity-display');
            const quantity = parseInt(quantityDisplay.textContent) || 1;
            
            // Check if item already exists in cart
            const existingCartItem = cart.find(item => item.id === itemId);
            
            if (existingCartItem) {
                // Item exists in cart, increment the quantity
                const newQuantity = existingCartItem.quantity + quantity;
                if (newQuantity <= 99) {
                    existingCartItem.quantity = newQuantity;
                    updateCartDisplay();
                    saveCartToStorage();
                    showCartNotification(`Added ${quantity} more ${existingCartItem.name} to cart!`);
                } else {
                    existingCartItem.quantity = 99;
                    updateCartDisplay();
                    saveCartToStorage();
                    showCartNotification(`Quantity limited to 99 for ${existingCartItem.name}`);
                }
            } else {
                // Item doesn't exist in cart, add new item
                const item = {
                    id: itemId,
                    name: this.getAttribute('data-name'),
                    price: parseFloat(this.getAttribute('data-price')),
                    image: this.getAttribute('data-image'),
                    description: this.getAttribute('data-description')
                };
                console.log(`Adding ${quantity} items to cart:`, item);
                updateCartItemQuantity(item, quantity);
            }
            
            // Always reset quantity display to 1 after adding to cart
            quantityDisplay.textContent = '1';
            
            // Update button states
            const minusBtn = this.closest('.food-menu-item').querySelector('.minus-btn');
            if (minusBtn) {
                minusBtn.style.opacity = '0.5';
                minusBtn.style.cursor = 'not-allowed';
            }
            
            updateFoodMenuQuantityDisplays();
        });
    });
}

// Function to update quantity displays in food menu
function updateFoodMenuQuantityDisplays() {
    console.log('updateFoodMenuQuantityDisplays called');
    console.log('Current cart:', cart);
    
    document.querySelectorAll('.quantity-display').forEach(display => {
        const itemId = display.getAttribute('data-id');
        const currentDisplayQuantity = parseInt(display.textContent) || 1;
        
        // Don't automatically update food menu quantities based on cart changes
        // Food menu quantities are independent and only change when user interacts with +/- buttons
        console.log(`Item ${itemId}: keeping current display quantity ${currentDisplayQuantity} (independent of cart)`);
        
        // Update button states based on current display quantity
        const minusBtn = display.parentElement.querySelector('.minus-btn');
        if (minusBtn) {
            const displayQuantity = parseInt(display.textContent) || 1;
            minusBtn.style.opacity = displayQuantity > 1 ? '1' : '0.5';
            minusBtn.style.cursor = displayQuantity > 1 ? 'pointer' : 'not-allowed';
        }
    });
}

// Debug function to help troubleshoot cart issues
function debugCart() {
    console.log('=== CART DEBUG INFO ===');
    console.log('Current cart array:', cart);
    console.log('Cart length (number of unique items):', cart.length);
    console.log('Total quantity in cart:', cart.reduce((sum, item) => sum + item.quantity, 0));
    console.log('LocalStorage foodCart:', localStorage.getItem('foodCart'));
    console.log('Cart count badges found:', document.querySelectorAll('[id*="cartItemCount"], .cart-count-badge').length);
    console.log('Floating cart count badge:', document.getElementById('floatingCartCount'));
    console.log('Food menu cart count badge:', document.getElementById('cartItemCount'));
    console.log('========================');
}

// Make debugCart available globally for browser console debugging
window.debugCart = debugCart;
window.updateCartCountBadge = updateCartCountBadge;
window.loadCartFromStorage = loadCartFromStorage;

// Function to show GCash QR Modal
function showGcashQrModal() {
    console.log('showGcashQrModal called');
    
    // Get the food service IP from window variable or use default
    let foodServiceIP = window.FOOD_SERVICE_IP || '192.168.1.12';
    // Handle case where foodServiceIP might be "None" string
    if (foodServiceIP === 'None' || foodServiceIP === 'null' || !foodServiceIP) {
        foodServiceIP = '192.168.1.12';
    }
    console.log('Using food service IP:', foodServiceIP);
    
    // First, ensure food menu modal has proper transition properties before hiding
    const foodMenuModal = document.getElementById('foodMenuModal');
    if (foodMenuModal && foodMenuModal.classList.contains('show')) {
        console.log('Preparing food menu modal for smooth transition...');
        
        // Ensure transition properties are set up properly
        foodMenuModal.style.transition = 'opacity 0.3s ease-in-out, visibility 0.3s ease-in-out';
        foodMenuModal.style.opacity = '1';
        foodMenuModal.style.visibility = 'visible';
        
        // Force a reflow to ensure the initial state is properly set
        foodMenuModal.offsetHeight;
        
        // Now smoothly hide the food menu modal
        foodMenuModal.style.opacity = '0';
        foodMenuModal.style.visibility = 'hidden';
    }
    
    // Check if modal already exists in the DOM
    let qrModal = document.getElementById('gcashQrModal');
    
    if (!qrModal) {
        console.log('Creating new QR modal...');
        // Create modal if it doesn't exist
        qrModal = document.createElement('div');
        qrModal.id = 'gcashQrModal';
        qrModal.className = 'modal fade';
        qrModal.setAttribute('tabindex', '-1');
        qrModal.setAttribute('aria-labelledby', 'gcashQrModalLabel');
        qrModal.setAttribute('aria-hidden', 'true');
        
        qrModal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header" style="background-color: #6D4C41; color: white;">
                        <h5 class="modal-title" id="gcashQrModalLabel">
                            <i class="fas fa-qrcode me-2"></i>GCash QR Code Payment
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body text-center">
                        <div class="alert alert-info mb-3">
                            <i class="fas fa-info-circle me-2"></i>
                            Scan this QR code using your GCash app to complete the payment.
                        </div>
                        <div class="qr-code-container mb-3">
                            <img src="http://${foodServiceIP}/online-food-ordering/assets/images/gcash-qr-code.png" 
                                 alt="GCash QR Code" 
                                 class="img-fluid" 
                                 style="max-width: 300px; border: 2px solid #e0e0e0; border-radius: 8px;"
                                 onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                            <div style="display:none; color:#666; padding: 20px; background:#f8f9fa; border-radius:8px;">
                                <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                                <p>QR code image not available.</p>
                                <p>Please contact support for payment instructions.</p>
                                <p><strong>Food Service IP:</strong> ${foodServiceIP}</p>
                            </div>
                        </div>
                        <div class="payment-details">
                            <p class="fw-bold mb-1">Account: FAWNA HOTEL</p>
                            <p class="mb-1">Number: 09932670873</p>
                            <p class="mb-0 text-muted">Please include your order reference in the payment note.</p>
                        </div>
                    </div>
                    <div class="modal-footer justify-content-center border-0">
                        <button type="button" class="btn btn-secondary px-4" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        `;
        
        // Add modal to body
        document.body.appendChild(qrModal);
        console.log('QR modal created and added to body');
    } else {
        console.log('QR modal already exists, updating IP...');
        // Update existing modal with correct IP
        const qrImage = qrModal.querySelector('img');
        if (qrImage) {
            qrImage.src = `http://${foodServiceIP}/online-food-ordering/assets/images/gcash-qr-code.png`;
        }
    }
    
    // Try multiple methods to show the modal
    console.log('Attempting to show modal...');
    
    // Method 1: Try Bootstrap Modal
    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
        console.log('Using Bootstrap Modal...');
        try {
            const modal = new bootstrap.Modal(qrModal, { 
                backdrop: 'static', 
                keyboard: true, 
                focus: true 
            });
            modal.show();
            console.log('Bootstrap modal.show() called');
        } catch (error) {
            console.error('Bootstrap Modal error:', error);
            showModalManually(qrModal);
        }
    } else {
        console.log('Bootstrap not available, using manual method...');
        showModalManually(qrModal);
    }
    
    // Add event listener to restore food menu modal when QR modal is closed
    qrModal.addEventListener('hidden.bs.modal', function() {
        if (foodMenuModal) {
            console.log('Restoring food menu modal smoothly...');
            
            // Ensure transition properties are set
            foodMenuModal.style.transition = 'opacity 0.3s ease-in-out, visibility 0.3s ease-in-out';
            foodMenuModal.style.visibility = 'visible';
            foodMenuModal.style.opacity = '0'; // Start from transparent
            
            // Force a reflow to ensure transition works
            foodMenuModal.offsetHeight;
            
            // Fade in smoothly
            foodMenuModal.style.opacity = '1';
        }
    });
    
    // Also add manual close handler
    const closeButtons = qrModal.querySelectorAll('[data-bs-dismiss="modal"], .btn-close');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (foodMenuModal) {
                console.log('Manual close: Restoring food menu modal smoothly...');
                
                // Ensure transition properties are set
                foodMenuModal.style.transition = 'opacity 0.3s ease-in-out, visibility 0.3s ease-in-out';
                foodMenuModal.style.visibility = 'visible';
                foodMenuModal.style.opacity = '0'; // Start from transparent
                
                // Force a reflow to ensure transition works
                foodMenuModal.offsetHeight;
                
                // Fade in smoothly
                foodMenuModal.style.opacity = '1';
            }
        });
    });
}

// Helper function to show modal manually
function showModalManually(modalElement) {
    console.log('Showing modal manually...');
    
    // Remove any existing backdrops
    const existingBackdrops = document.querySelectorAll('.modal-backdrop');
    existingBackdrops.forEach(backdrop => backdrop.remove());
    
    // Set high z-index to ensure modal appears on top
    modalElement.style.zIndex = '9999';
    modalElement.style.display = 'block';
    modalElement.classList.add('show');
    document.body.classList.add('modal-open');
    
    // Add backdrop with high z-index
    const backdrop = document.createElement('div');
    backdrop.className = 'modal-backdrop fade show';
    backdrop.style.zIndex = '9998';
    document.body.appendChild(backdrop);
    
    // Add close functionality
    const closeButtons = modalElement.querySelectorAll('[data-bs-dismiss="modal"], .btn-close');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            hideModalManually(modalElement, backdrop);
            // Restore food menu modal visibility
            const foodMenuModal = document.getElementById('foodMenuModal');
            if (foodMenuModal) {
                console.log('Manual modal close: Restoring food menu modal smoothly...');
                
                // Ensure transition properties are set
                foodMenuModal.style.transition = 'opacity 0.3s ease-in-out, visibility 0.3s ease-in-out';
                foodMenuModal.style.visibility = 'visible';
                foodMenuModal.style.opacity = '0'; // Start from transparent
                
                // Force a reflow to ensure transition works
                foodMenuModal.offsetHeight;
                
                // Fade in smoothly
                foodMenuModal.style.opacity = '1';
            }
        });
    });
    
    // Close on backdrop click
    backdrop.addEventListener('click', function() {
        hideModalManually(modalElement, backdrop);
        // Restore food menu modal visibility
        const foodMenuModal = document.getElementById('foodMenuModal');
        if (foodMenuModal) {
            console.log('Backdrop click: Restoring food menu modal smoothly...');
            
            // Ensure transition properties are set
            foodMenuModal.style.transition = 'opacity 0.3s ease-in-out, visibility 0.3s ease-in-out';
            foodMenuModal.style.visibility = 'visible';
            foodMenuModal.style.opacity = '0'; // Start from transparent
            
            // Force a reflow to ensure transition works
            foodMenuModal.offsetHeight;
            
            // Fade in smoothly
            foodMenuModal.style.opacity = '1';
        }
    });
    
    console.log('Modal shown manually with high z-index');
}

// Helper function to hide modal manually
function hideModalManually(modalElement, backdrop) {
    modalElement.style.display = 'none';
    modalElement.classList.remove('show');
    document.body.classList.remove('modal-open');
    if (backdrop) {
        backdrop.remove();
    }
}



// Test function to clear cart
window.testClearCart = function() {
    clearCart();
    console.log('Cart cleared');
    updateCartCountBadge();
};
