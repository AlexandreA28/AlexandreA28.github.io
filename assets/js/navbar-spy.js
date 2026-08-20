const sections = document.querySelectorAll('header[id], section[id]');
const navLinks = document.querySelectorAll('.nav-links a');

const observerOptions = {
    root: null,
    
    rootMargin: "-15% 0px -85% 0px", 
    threshold: 0
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const id = entry.target.getAttribute('id');

            history.replaceState(null, null, `#${id}`);
            navLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${id}`) {
                    link.classList.add('active');
                }
            });
        }
    });
}, observerOptions);

sections.forEach(section => {
    observer.observe(section);
});