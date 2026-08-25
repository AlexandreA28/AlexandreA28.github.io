// Fonction asynchrone pour compter les Write-Ups
async function updateWUCount(pageUrl, targetId) {
    try {
        const response = await fetch(pageUrl);
        if (!response.ok) throw new Error("Page introuvable");
        const html = await response.text();

        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');

        // 👇 LA MODIFICATION EST ICI : on compte les '.card-wu' au lieu des '.decrypt-zone'
        const count = doc.querySelectorAll('.card-wu').length;

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
    updateWUCount('root-me/forensic/index.html', 'count-forensic');
    updateWUCount('root-me/web-client/index.html', 'count-web');
});