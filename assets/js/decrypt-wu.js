async function decryptWU(zoneId, inputId, base64Data) {
    const password = document.getElementById(inputId).value;
    const errorMsg = document.getElementById(zoneId.replace('zone', 'error'));
    errorMsg.style.display = 'none';

    try {
        const binaryString = atob(base64Data);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }

        const salt = bytes.slice(0, 16);
        const nonce = bytes.slice(16, 28);
        const ciphertext = bytes.slice(28);

        const enc = new TextEncoder();
        const keyMaterial = await window.crypto.subtle.importKey(
            "raw",
            enc.encode(password),
            { name: "PBKDF2" },
            false,
            ["deriveKey"]
        );

        const aesKey = await window.crypto.subtle.deriveKey(
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
            aesKey,
            ciphertext
        );

        const dec = new TextDecoder();
        document.getElementById(zoneId).innerHTML = dec.decode(decryptedBuffer);

    } catch (e) {
        console.error("Échec du déchiffrement", e);
        errorMsg.style.display = 'block';
    }
}