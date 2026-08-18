const backToTopBtn = document.getElementById('backToTop');

if (backToTopBtn) {
    // 1. Afficher ou masquer le bouton selon le scroll
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            backToTopBtn.classList.add('show');
        } else {
            backToTopBtn.classList.remove('show');
        }
    });

    // 2. Remonter en douceur vers la section #home au clic
    backToTopBtn.addEventListener('click', (e) => {
        e.preventDefault();
        
        // On cible directement la section home
        const homeSection = document.getElementById('home');
        if (homeSection) {
            homeSection.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
}