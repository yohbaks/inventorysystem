// ==================== PREMIUM NAVBAR FUNCTIONALITY ====================

$(document).ready(function() {
  
  // Initialize tooltips
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Theme Toggle Functionality
  const themeToggle = document.getElementById('themeToggle');
  if (themeToggle) {
    // Check for saved theme preference or default to 'light'
    const currentTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    
    // Update icon based on current theme
    updateThemeIcon(currentTheme);

    themeToggle.addEventListener('click', function() {
      let theme = document.documentElement.getAttribute('data-theme');
      let newTheme = theme === 'dark' ? 'light' : 'dark';
      
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('theme', newTheme);
      updateThemeIcon(newTheme);
      
      // Add smooth transition effect
      document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
      setTimeout(() => {
        document.body.style.transition = '';
      }, 300);
    });
  }

  function updateThemeIcon(theme) {
    const icon = themeToggle.querySelector('i');
    if (theme === 'dark') {
      icon.classList.remove('fa-moon');
      icon.classList.add('fa-sun');
    } else {
      icon.classList.remove('fa-sun');
      icon.classList.add('fa-moon');
    }
  }

  // Search Input Focus with Keyboard Shortcut (Ctrl+K)
  document.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      const searchInput = document.querySelector('.premium-search-input');
      if (searchInput) {
        searchInput.focus();
      }
    }
  });

  // Search Input Animation
  const searchInput = document.querySelector('.premium-search-input');
  if (searchInput) {
    searchInput.addEventListener('focus', function() {
      this.parentElement.classList.add('search-focused');
    });
    
    searchInput.addEventListener('blur', function() {
      this.parentElement.classList.remove('search-focused');
    });
  }

  // Notification Mark as Read
  $('.premium-notification-item.unread').on('click', function(e) {
    $(this).removeClass('unread');
  });

  // Update Live Stats (Example - replace with real API calls)
  function updateLiveStats() {
    // This would normally fetch from your backend
    // Example animation for stat values
    $('.stat-value').each(function() {
      const $this = $(this);
      const countTo = parseInt($this.text().replace(/,/g, ''));
      
      $({ countNum: 0 }).animate({
        countNum: countTo
      }, {
        duration: 1000,
        easing: 'swing',
        step: function() {
          $this.text(Math.floor(this.countNum).toLocaleString());
        },
        complete: function() {
          $this.text(countTo.toLocaleString());
        }
      });
    });
  }

  // Initialize stats animation on page load
  // updateLiveStats();

  // Close dropdowns when clicking outside
  $(document).on('click', function(e) {
    if (!$(e.target).closest('.dropdown').length) {
      $('.dropdown-menu').removeClass('show');
    }
  });

  // Smooth scroll for notification items
  $('.premium-notifications-scroll').on('scroll', function() {
    const scrollTop = $(this).scrollTop();
    if (scrollTop > 0) {
      $(this).addClass('is-scrolled');
    } else {
      $(this).removeClass('is-scrolled');
    }
  });

  // Add loading state to quick action cards
  $('.quick-action-card').on('click', function(e) {
    const $this = $(this);
    const $icon = $this.find('.quick-action-icon');
    
    // Add loading spinner
    const originalIcon = $icon.html();
    $icon.html('<i class="fas fa-spinner fa-spin"></i>');
    
    // Remove loading state after navigation (for visual feedback)
    setTimeout(() => {
      $icon.html(originalIcon);
    }, 500);
  });

  // Notification counter animation
  function animateNotificationBadge() {
    $('.notification-badge').each(function() {
      $(this).addClass('pulse');
    });
  }

  // Profile dropdown enhancement
  $('.premium-profile-btn').on('click', function() {
    $(this).addClass('profile-clicked');
    setTimeout(() => {
      $(this).removeClass('profile-clicked');
    }, 300);
  });

  // Add ripple effect to icon buttons
  $('.premium-icon-btn').on('click', function(e) {
    const $button = $(this);
    const $ripple = $('<span class="ripple"></span>');
    
    $button.append($ripple);
    
    setTimeout(() => {
      $ripple.remove();
    }, 600);
  });

  // Auto-hide notifications after viewing
  let notificationTimeout;
  $('#notificationDropdown').on('shown.bs.dropdown', function() {
    notificationTimeout = setTimeout(() => {
      // Mark all as seen after 3 seconds
      $('.premium-notification-item.unread').each(function() {
        $(this).fadeOut(200, function() {
          $(this).removeClass('unread').fadeIn(200);
        });
      });
    }, 3000);
  });

  $('#notificationDropdown').on('hidden.bs.dropdown', function() {
    clearTimeout(notificationTimeout);
  });

  // Add entrance animation to dropdowns
  $('.dropdown').on('show.bs.dropdown', function() {
    $(this).find('.dropdown-menu').addClass('animated fadeIn faster');
  });

  $('.dropdown').on('hide.bs.dropdown', function() {
    $(this).find('.dropdown-menu').removeClass('animated fadeIn faster');
  });

  console.log('Premium Navbar initialized successfully! ✨');
});

// Add ripple effect CSS dynamically
const rippleStyle = document.createElement('style');
rippleStyle.textContent = `
  .ripple {
    position: absolute;
    border-radius: 50%;
    background: rgba(108, 92, 231, 0.3);
    width: 20px;
    height: 20px;
    animation: ripple-animation 0.6s ease-out;
    pointer-events: none;
  }

  @keyframes ripple-animation {
    to {
      transform: scale(4);
      opacity: 0;
    }
  }

  .profile-clicked {
    animation: profile-pulse 0.3s ease;
  }

  @keyframes profile-pulse {
    0% { transform: scale(1); }
    50% { transform: scale(0.95); }
    100% { transform: scale(1); }
  }

  .search-focused {
    animation: search-glow 0.3s ease-in-out;
  }

  @keyframes search-glow {
    0% { transform: scale(1); }
    50% { transform: scale(1.02); }
    100% { transform: scale(1); }
  }
`;
document.head.appendChild(rippleStyle);