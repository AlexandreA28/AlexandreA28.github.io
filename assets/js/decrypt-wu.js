let currentFilename = "";

// 1. Ouvrir la modale
function openModal(title, filename) {
    document.getElementById('modal-title').innerText = title;
    currentFilename = filename;
    
    // On réinitialise l'affichage (montre le formulaire, cache le texte)
    document.getElementById('modal-decrypt-form').style.display = 'block';
    document.getElementById('modal-decrypted-content').style.display = 'none';
    document.getElementById('modal-flag-input').value = '';
    
    // On affiche la modale (Flexbox pour centrer)
    document.getElementById('wu-modal-overlay').style.display = 'flex';
    
    // On focus automatiquement l'input pour que l'utilisateur puisse taper direct
    setTimeout(() => document.getElementById('modal-flag-input').focus(), 100);
}

// 2. Fermer la modale
function closeModal() {
    document.getElementById('wu-modal-overlay').style.display = 'none';
}

// 3. Fonction de déchiffrement (avec WebCrypto)
async function attemptDecrypt() {
    const modalBox = document.getElementById('wu-modal-box');
    const password = document.getElementById('modal-flag-input').value;

    try {
        // --- LOGIQUE WEB CRYPTO EXACTEMENT COMME AVANT ---
        const response = await fetch(currentFilename);
        if (!response.ok) throw new Error("Fichier introuvable.");
        const base64Data = await response.text();

        const binary_string = window.atob(base64Data.trim());
        const encryptedBytes = new Uint8Array(binary_string.length);
        for (let i = 0; i < binary_string.length; i++) encryptedBytes[i] = binary_string.charCodeAt(i);

        const salt = encryptedBytes.slice(0, 16);
        const nonce = encryptedBytes.slice(16, 28);
        const ciphertext = encryptedBytes.slice(28);

        const enc = new TextEncoder();
        const keyMaterial = await window.crypto.subtle.importKey("raw", enc.encode(password), { name: "PBKDF2" }, false, ["deriveKey"]);
        const key = await window.crypto.subtle.deriveKey(
            { name: "PBKDF2", salt: salt, iterations: 600000, hash: "SHA-256" },
            keyMaterial, { name: "AES-GCM", length: 256 }, false, ["decrypt"]
        );

        const decryptedBuffer = await window.crypto.subtle.decrypt({ name: "AES-GCM", iv: nonce }, key, ciphertext);
        
        const dec = new TextDecoder();
        const decryptedHtml = dec.decode(decryptedBuffer);
        
        // --- SUCCÈS : On remplace et on affiche le WU ---
        document.getElementById('modal-decrypted-content').innerHTML = decryptedHtml;
        document.getElementById('modal-decrypt-form').style.display = 'none';
        document.getElementById('modal-decrypted-content').style.display = 'block';

    } catch (e) {
        // --- ÉCHEC : On déclenche l'animation d'erreur ---
        console.error("Échec du déchiffrement");
        
        // On retire la classe puis on la remet pour pouvoir rejouer l'animation si le user se trompe plusieurs fois
        modalBox.classList.remove('error-trigger');
        void modalBox.offsetWidth; // Astuce JS pour forcer le navigateur à "recharger" l'élément
        modalBox.classList.add('error-trigger');
    }
}