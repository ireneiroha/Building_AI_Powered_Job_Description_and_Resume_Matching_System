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


