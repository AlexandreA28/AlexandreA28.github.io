// Fonction utilitaire pour convertir le Base64 en tableau d'octets
function base64ToUint8Array(base64) {
    const binary_string = window.atob(base64);
    const len = binary_string.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
        bytes[i] = binary_string.charCodeAt(i);
    }
    return bytes;
}

// Fonction principale de déchiffrement
async function decryptWU(zoneId, inputId, filename) {
    const errorEl = document.getElementById(zoneId.replace('zone', 'error'));
    errorEl.style.display = 'none';

    try {
        const response = await fetch(filename);
        if (!response.ok) throw new Error("Fichier introuvable.");
        const base64Data = await response.text();

        const encryptedBytes = base64ToUint8Array(base64Data.trim());
        if (encryptedBytes.length < 28) throw new Error("Fichier corrompu.");

        const salt = encryptedBytes.slice(0, 16);
        const nonce = encryptedBytes.slice(16, 28);
        const ciphertext = encryptedBytes.slice(28);

        const password = document.getElementById(inputId).value;
        const enc = new TextEncoder();
        
        const keyMaterial = await window.crypto.subtle.importKey(
            "raw",
            enc.encode(password),
            { name: "PBKDF2" },
            false,
            ["deriveKey"]
        );

        const key = await window.crypto.subtle.deriveKey(
            {
                name: "PBKDF2",
                salt: salt,
                iterations: 600000,
                hash: "SHA-256"
            },
            keyMaterial,
            { name: "AES-GCM", length: 256 },
            false,
            ["decrypt"]
        );

        const decryptedBuffer = await window.crypto.subtle.decrypt(
            { name: "AES-GCM", iv: nonce },
            key,
            ciphertext
        );

        const dec = new TextDecoder();
        const decryptedHtml = dec.decode(decryptedBuffer);
        
        const zone = document.getElementById(zoneId);
        zone.innerHTML = decryptedHtml;

    } catch (e) {
        console.error("Erreur de déchiffrement :", e);
        errorEl.style.display = 'block';
    }
}