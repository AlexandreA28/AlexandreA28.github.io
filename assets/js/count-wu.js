// Fonction asynchrone pour compter les Write-Ups
async function updateWUCount(pageUrl, targetId) {
    try {
        const response = await fetch(pageUrl);
        if (!response.ok) throw new Error("Page introuvable");
        const html = await response.text();

        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');

        const count = doc.querySelectorAll('.card-wu-list').length;

        const badge = document.getElementById(targetId);
        if (badge) {
            badge.innerText = `${count} Write-Ups`;
        }
    } catch (error) {
        console.warn(`Impossible de compter les WUs pour ${pageUrl}`);
        document.getElementById(targetId).style.display = 'none'; 
    }
}

// On lance les requêtes dès que la page principale a fini de charger
document.addEventListener("DOMContentLoaded", () => {
    updateWUCount('root-me/app-script/index.html', 'count-app-script');
    updateWUCount('root-me/cracking/index.html', 'count-cracking');
    updateWUCount('root-me/forensic/index.html', 'count-forensic');
    updateWUCount('root-me/programmation/index.html', 'count-programmation');
    updateWUCount('root-me/realiste/index.html', 'count-realiste');
    updateWUCount('root-me/steganographie/index.html', 'count-steganographie');
    updateWUCount('root-me/web-client/index.html', 'count-web');
});