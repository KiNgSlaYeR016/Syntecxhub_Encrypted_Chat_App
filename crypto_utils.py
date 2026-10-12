# Shared encryption helpers used by both the server and client
# Keeps the AES/IV logic in one place instead of duplicating it

import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, padding

FIXED_SALT = b"syntecxhub-fixed-salt-16"  # must be identical and known on both sides
ITERATIONS = 200_000


def derive_key(passphrase):
    # turns the shared passphrase into a proper 32-byte AES key
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=FIXED_SALT,
        iterations=ITERATIONS,
    )
    key = kdf.derive(passphrase.encode())
    return key, FIXED_SALT


def encrypt_message(plaintext, key):
    # every message gets its own random IV - this is the "safe IV usage" part of the task
    iv = os.urandom(16)

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext.encode()) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    # send the IV along with the ciphertext - IV isn't secret, just needs to be unique
    return iv + ciphertext


def decrypt_message(packet, key):
    iv = packet[:16]
    ciphertext = packet[16:]

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_data) + unpadder.finalize()

    return plaintext.decode()