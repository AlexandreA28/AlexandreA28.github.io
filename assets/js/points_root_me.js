document.addEventListener("DOMContentLoaded", () => {
    fetch('stats.json')
        .then(response => response.json())
        .then(data => {
            document.getElementById('rm-points').textContent = data.points;
            document.getElementById('rm-rank').textContent = data.rank;
        })
        .catch(error => {
            console.error("Impossible de charger les stats Root-Me:", error);
            document.getElementById('rm-points').textContent = "N/A";
            document.getElementById('rm-rank').textContent = "N/A";
        });
});