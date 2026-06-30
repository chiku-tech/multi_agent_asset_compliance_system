/* Sidebar Component - Asset Compliance AI */

(function () {
  const Sidebar = {
    init() {
      // Setup Logout button handler
      const logoutBtn = document.getElementById('sidebar-logout-btn');
      if (logoutBtn) {
        // Remove existing listener if any (to prevent multiple event firing)
        const newLogoutBtn = logoutBtn.cloneNode(true);
        logoutBtn.parentNode.replaceChild(newLogoutBtn, logoutBtn);
        
        newLogoutBtn.addEventListener('click', (e) => {
          e.preventDefault();
          
          if (window.Modal) {
            window.Modal.create({
              title: 'Confirm Sign Out',
              content: 'Are you sure you want to sign out? Your API key will be cleared from local storage.',
              confirmText: 'Sign Out',
              cancelText: 'Cancel',
              variant: 'danger',
              onConfirm: (close) => {
                if (window.Config) {
                  window.Config.set('apiKey', '');
                  window.Config.addActivity('Authentication', 'User manually signed out', 'info');
                }
                close();
                window.location.hash = '#/login';
              }
            });
          } else {
            // Fallback if Modal is not loaded
            if (confirm('Sign out of Asset Compliance AI?')) {
              if (window.Config) {
                window.Config.set('apiKey', '');
              }
              window.location.hash = '#/login';
            }
          }
        });
      }

      // Handle mobile responsive navigation sidebar toggle
      const mobileToggle = document.getElementById('mobile-sidebar-toggle');
      const sidebarContainer = document.querySelector('.sidebar-container');
      if (mobileToggle && sidebarContainer) {
        mobileToggle.onclick = () => {
          sidebarContainer.classList.toggle('active');
        };
        
        // Close sidebar on navigate in mobile view
        const navLinks = document.querySelectorAll('.sidebar-nav-link');
        navLinks.forEach(link => {
          link.addEventListener('click', () => {
            sidebarContainer.classList.remove('active');
          });
        });
      }
    }
  };

  window.Sidebar = Sidebar;
  
  // Run on layout initialization
  document.addEventListener('DOMContentLoaded', () => {
    Sidebar.init();
  });
})();
