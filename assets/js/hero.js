const hero = document.querySelector('.hero');

if (hero) {
    const spawnBoxSize = 600; 
    
    let cursorX = -1000;
    let cursorY = -1000;
    let lastParticleX = 0;
    let lastParticleY = 0;
    const minDistance = 50;

    const createParticle = () => {

        const rect = hero.getBoundingClientRect();

        if (
            cursorX < rect.left || 
            cursorX > rect.right || 
            cursorY < rect.top || 
            cursorY > rect.bottom
        ) {
            return;
        }

        const mouseX = cursorX - rect.left;
        const mouseY = cursorY - rect.top;

        const distance = Math.hypot(mouseX - lastParticleX, mouseY - lastParticleY);
        
        if (distance < minDistance) return;

        lastParticleX = mouseX;
        lastParticleY = mouseY;

        const particle = document.createElement('div');
        particle.classList.add('glitch-particle');

        let size = Math.random() * 30 + 10; 
        if (Math.random() > 0.9) { size = Math.random() * 60 + 10; }
        
        let width, height;
        const shapeType = Math.random();
        
        if (shapeType < 0.33) {
            width = Math.min(size, 35); 
            height = Math.min(size, 35);
        } else if (shapeType < 0.66) {
            width = size * 2.5; height = size * 0.2;
        } else {
            width = size * 0.2; height = size * 2;
        }

        particle.style.width = `${width}px`;
        particle.style.height = `${height}px`;

        particle.style.backgroundColor = 'rgba(0, 191, 255, 0.05)';
        const offset = Math.max(2, size * 0.05); 
        particle.style.setProperty('--offset', `${offset}px`);

        const offsetX = (Math.random() - 0.5) * spawnBoxSize;
        const offsetY = (Math.random() - 0.5) * spawnBoxSize;

        particle.style.left = `${mouseX + offsetX - (width / 2)}px`;
        particle.style.top = `${mouseY + offsetY - (height / 2)}px`;

        hero.appendChild(particle);

        setTimeout(() => {
            particle.remove();
        }, 300);
    };

    window.addEventListener('mousemove', (e) => {
        cursorX = e.clientX;
        cursorY = e.clientY;
        createParticle();
    });

    window.addEventListener('scroll', () => {
        createParticle();
    });
}