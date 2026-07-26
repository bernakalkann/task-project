import json
import base64
import hashlib
import os
from django.conf import settings
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

def get_encryption_key_bytes():
    raw_key = getattr(settings, 'ENCRYPTION_KEY', 'task_collaboration_secret_key_32b')
    # 32 byte key (AES-256) via SHA-256
    return hashlib.sha256(raw_key.encode('utf-8')).digest()

def encrypt_data(data):
    """
    Python dict/list/string verisini AES-256-CBC ile şifreler ve Base64 formatında döner.
    Network isteklerinde şifrelenmiş veri olarak gözükür.
    """
    key = get_encryption_key_bytes()
    iv = os.urandom(16)
    
    json_str = json.dumps(data, ensure_ascii=False)
    data_bytes = json_str.encode('utf-8')

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data_bytes) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    return {
        'encrypted_data': base64.b64encode(ciphertext).decode('utf-8'),
        'iv': base64.b64encode(iv).decode('utf-8'),
        'is_encrypted': True
    }

def decrypt_data(encrypted_payload):
    """
    Şifrelenmiş payload'u çözer ve Python objesine çevirir.
    """
    key = get_encryption_key_bytes()
    ciphertext = base64.b64decode(encrypted_payload['encrypted_data'])
    iv = base64.b64decode(encrypted_payload['iv'])

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    data_bytes = unpadder.update(padded_data) + unpadder.finalize()

    return json.loads(data_bytes.decode('utf-8'))
