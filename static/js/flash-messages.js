document.addEventListener('DOMContentLoaded', function() {
    // Function to handle message dismissal
    function setupMessageDismissal(message) {
        // Add close button if not exists
        if (!message.querySelector('.close-btn')) {
            const closeBtn = document.createElement('button');
            closeBtn.classList.add('close-btn');
            closeBtn.innerHTML = '&times;';
            closeBtn.style.cssText = `
                float: right;
                background: none;
                border: none;
                font-size: 20px;
                margin-left: 10px;
                cursor: pointer;
                color: inherit;
                opacity: 0.7;
                padding: 0;
                line-height: 1;
            `;
            closeBtn.addEventListener('mouseenter', function() {
                this.style.opacity = '1';
            });
            closeBtn.addEventListener('mouseleave', function() {
                this.style.opacity = '0.7';
            });
            closeBtn.addEventListener('click', function() {
                fadeOut(message);
            });
            message.insertBefore(closeBtn, message.firstChild);
        }

        // Set auto-dismiss timeout
        setTimeout(() => fadeOut(message), 3000);
    }

    // Function to fade out and remove an element
    function fadeOut(element) {
        element.style.transition = 'opacity 500ms ease';
        element.style.opacity = '0';
        setTimeout(() => {
            if (element && element.parentNode) {
                element.parentNode.removeChild(element);
            }
        }, 500);
    }

    // Handle all alert messages
    document.querySelectorAll('.alert, .alert-warning, .alert-success, .alert-danger, .alert-info, [role="alert"]').forEach(setupMessageDismissal);
}); 