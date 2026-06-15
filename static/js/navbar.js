(() => {
    // Elements
    const mobileBtn = document.getElementById('mobile-menu-toggle');
    const mobileMenu = document.getElementById('mobile-menu');
    const userBtn = document.getElementById('user-menu-btn');
    const userDropdown = document.getElementById('user-dropdown');

    // MOBILE MENU
    if (mobileBtn && mobileMenu) {
        mobileBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const isHidden = mobileMenu.classList.toggle('hidden');

            mobileBtn.querySelector('.material-symbols-outlined')
                .textContent = isHidden ? 'menu' : 'close';

            userDropdown?.classList.add('hidden');
        });
    }

    // USER DROPDOWN
    if (userBtn && userDropdown) {
        userBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            userDropdown.classList.toggle('hidden');
            mobileMenu?.classList.add('hidden');
        });
    }

    // CLOSE ON OUTSIDE CLICK
    window.addEventListener('click', () => {
        userDropdown?.classList.add('hidden');
        mobileMenu?.classList.add('hidden');
        if (mobileBtn) {
            mobileBtn.querySelector('.material-symbols-outlined').textContent = 'menu';
        }
    });

    // RESPONSIVE RESET
    window.addEventListener('resize', () => {
        if (window.innerWidth >= 1024 && mobileMenu) {
            mobileMenu.classList.add('hidden');
            document.body.style.overflow = '';
        }
    });

})();
