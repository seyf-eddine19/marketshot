(() => {
    // Elements
    const themeBtns = [
        document.getElementById('theme-toggle'),
        document.getElementById('theme-toggle-mobile')
    ];


    // THEME TOGGLE
    function updateThemeIcons() {
        const isDark = document.documentElement.classList.contains('dark');

        document.querySelectorAll('.theme-toggle-dark-icon')
            .forEach(el => el.classList.toggle('hidden', isDark));

        document.querySelectorAll('.theme-toggle-light-icon')
            .forEach(el => el.classList.toggle('hidden', !isDark));
    }

    themeBtns.forEach(btn => {
        if (!btn) return;

        btn.addEventListener('click', (e) => {
            e.stopPropagation();

            const isDark = document.documentElement.classList.toggle('dark');
            localStorage.setItem('color-theme', isDark ? 'dark' : 'light');

            updateThemeIcons();
        });
    });

    updateThemeIcons();
})();