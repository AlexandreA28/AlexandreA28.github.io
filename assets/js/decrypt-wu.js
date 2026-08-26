let currentFilename = "";

// 1. Ouvrir la modale
function openModal(title, filename) {
    document.getElementById('modal-title').innerText = title;
    currentFilename = filename;
    
    document.getElementById('modal-decrypt-form').style.display = 'block';
    document.getElementById('modal-decrypted-content').style.display = 'none';
    document.getElementById('modal-flag-input').value = '';
    document.getElementById('wu-modal-overlay').style.display = 'flex';

    document.body.style.overflow = 'hidden';
    
    setTimeout(() => document.getElementById('modal-flag-input').focus(), 100);
}

// 2. Fermer la modale
function closeModal() {
    document.getElementById('wu-modal-overlay').style.display = 'none';
    document.body.style.overflow = 'auto';
}

// 3. Fonction de déchiffrement
async function attemptDecrypt() {
    const modalBox = document.getElementById('wu-modal-box');
    const password = document.getElementById('modal-flag-input').value;

    try {
        // --- LOGIQUE WEB CRYPTO ---
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
        
        document.getElementById('modal-decrypted-content').innerHTML = decryptedHtml
        document.getElementById('modal-decrypt-form').style.display = 'none';
        document.getElementById('modal-decrypted-content').style.display = 'block';

    } catch (e) {
        console.error("Échec du déchiffrement");
        modalBox.classList.remove('error-trigger');
        void modalBox.offsetWidth;
        modalBox.classList.add('error-trigger');
    }
}