document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('.upload-form');
    const toggleButton = document.querySelector('.menu-toggle');
    const menuContent = document.querySelector('.menu-content');
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    let isDarkMode = false;

    // Password toggle functionality
    document.querySelectorAll('.password-container .fa-eye').forEach(eye => {
        const password = eye.previousElementSibling;
        eye.addEventListener('click', () => {
            const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
            password.setAttribute('type', type);
            eye.classList.toggle('fa-eye-slash');
        });
    });

    form.addEventListener('submit', (e) => {
        const jobDesc = form.querySelector('textarea').value;
        if (!jobDesc.trim()) {
            e.preventDefault();
            alert('Please enter a job description.');
        }
    });

    toggleButton.addEventListener('click', (e) => {
        e.stopPropagation();
        menuContent.classList.toggle('active');
    });

    // Toggle settings dropdown on click
    document.querySelectorAll('.settings-toggle').forEach(toggle => {
        toggle.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const dropdown = toggle.nextElementSibling;
            dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
        });
    });

    darkModeToggle.addEventListener('click', () => {
        isDarkMode = !isDarkMode;
        document.body.setAttribute('data-theme', isDarkMode ? 'dark' : 'light');
    });

    // Close menu and dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!toggleButton.contains(e.target) && !menuContent.contains(e.target)) {
            menuContent.classList.remove('active');
            document.querySelectorAll('.settings-dropdown').forEach(dropdown => {
                dropdown.style.display = 'none';
            });
        }
    });
});

// Function to fetch notification count and update badges
async function fetchNotificationCount() {
    try {
        const response = await fetch('/api/notifications');
        if (!response.ok) {
            if (response.status === 401) {
                console.warn("User not authenticated for notifications. Redirecting to login.");
                window.location.href = '/login'; 
                return;
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        if (data.unread_count !== undefined) {
            const count = data.unread_count;
            const headerBadge = document.getElementById('header-notification-count');
            const sidebarBadge = document.getElementById('sidebar-notification-count');

            if (headerBadge) {
                headerBadge.textContent = count;
                headerBadge.style.display = count > 0 ? 'inline-block' : 'none'; // Show if count > 0
            }
            if (sidebarBadge) {
                sidebarBadge.textContent = count;
                sidebarBadge.style.display = count > 0 ? 'inline-block' : 'none'; // Show if count > 0
            }
        }
    } catch (error) {
        console.error('Error fetching notification count:', error);
    }
}

// Function to mark a notification as read
async function markNotificationAsRead(notificationId) {
    try {
        const response = await fetch(`/api/notifications/mark_read/${notificationId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        if (!response.ok) {
            if (response.status === 401) {
                console.warn("User not authenticated for marking notifications. Redirecting to login.");
                window.location.href = '/login';
                return false;
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        if (data.message) {
            console.log(data.message);
            fetchNotificationCount();
            return true;
        } else if (data.error) {
            console.error('Error marking notification as read:', data.error);
            return false;
        }
    } catch (error) {
        console.error('Error in markNotificationAsRead:', error);
        return false;
    }
}


// Event listeners for DOM content loaded for notification features
document.addEventListener('DOMContentLoaded', function() {
    fetchNotificationCount();

    const notificationItems = document.querySelectorAll('.notification-item');
    notificationItems.forEach(item => {
        item.addEventListener('click', async function() {
            const notificationId = this.dataset.notificationId;
            const isRead = this.dataset.isRead === 'true'; // dataset values are strings, so compare to 'true'

            if (!isRead) {
                const success = await markNotificationAsRead(notificationId);
                if (success) {
                    this.classList.add('read');
                    this.dataset.isRead = 'true'; 
                }
            }
        });
    });
});
