window.addEventListener('load', () => {
    const loader = document.getElementById('loader');
    
    if (loader) {
        // On ajoute un tout petit délai (ex: 400ms) pour que l'animation ait le temps de s'apprécier
        setTimeout(() => {
            loader.classList.add('hidden');
        }, 400);
    }
});