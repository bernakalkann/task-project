const ENCRYPTION_KEY = 'task_collaboration_secret_key_32b';

async function getKey() {
  const enc = new TextEncoder();
  const keyData = enc.encode(ENCRYPTION_KEY);
  const hash = await window.crypto.subtle.digest('SHA-256', keyData);
  return window.crypto.subtle.importKey(
    'raw',
    hash,
    { name: 'AES-CBC' },
    false,
    ['encrypt', 'decrypt']
  );
}

function base64ToBuffer(base64) {
  const binaryString = window.atob(base64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes.buffer;
}

function bufferToBase64(buffer) {
  let binary = '';
  const bytes = new Uint8Array(buffer);
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return window.btoa(binary);
}

export async function decryptData(encryptedPayload) {
  if (!encryptedPayload || !encryptedPayload.encrypted_data || !encryptedPayload.iv) {
    return encryptedPayload;
  }
  try {
    const key = await getKey();
    const iv = base64ToBuffer(encryptedPayload.iv);
    const ciphertext = base64ToBuffer(encryptedPayload.encrypted_data);

    const decryptedBuffer = await window.crypto.subtle.decrypt(
      { name: 'AES-CBC', iv: new Uint8Array(iv) },
      key,
      ciphertext
    );

    const dec = new TextDecoder();
    const jsonString = dec.decode(decryptedBuffer);
    return JSON.parse(jsonString);
  } catch (error) {
    console.error('Şifre çözme hatası:', error);
    throw error;
  }
}

export async function encryptData(data) {
  try {
    const key = await getKey();
    const iv = window.crypto.getRandomValues(new Uint8Array(16));
    const enc = new TextEncoder();
    const jsonString = JSON.stringify(data);
    const dataBuffer = enc.encode(jsonString);

    const encryptedBuffer = await window.crypto.subtle.encrypt(
      { name: 'AES-CBC', iv },
      key,
      dataBuffer
    );

    return {
      encrypted_data: bufferToBase64(encryptedBuffer),
      iv: bufferToBase64(iv),
      is_encrypted: true
    };
  } catch (error) {
    console.error('Şifreleme hatası:', error);
    throw error;
  }
}
