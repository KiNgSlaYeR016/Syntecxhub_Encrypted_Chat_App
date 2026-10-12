# Encrypted chat client
# Connects to the server, encrypts every message before sending,
# and runs a separate thread to listen for incoming messages at the same time.

import socket
import threading
from crypto_utils import encrypt_message, decrypt_message, derive_key

HOST = "127.0.0.1"
PORT = 5050
PRE_SHARED_PASSPHRASE = "syntecxhub-week2"  # must match the server exactly

key, salt = derive_key(PRE_SHARED_PASSPHRASE)


def listen_for_messages(sock):
    while True:
        try:
            raw = sock.recv(4096)
            if not raw:
                print("\nDisconnected from server.")
                break
            message = decrypt_message(raw, key)
            print(f"\n{message}\n> ", end="")
        except Exception:
            print("\nConnection lost.")
            break


def start_client():
    nickname = input("Choose a nickname: ").strip()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    # send nickname first, encrypted, so the server knows who we are
    sock.sendall(encrypt_message(nickname, key))

    # listen for incoming messages on a background thread so we can type and receive at once
    listener = threading.Thread(target=listen_for_messages, args=(sock,), daemon=True)
    listener.start()

    print("Connected. Type a message and press Enter (type 'exit' to quit).")
    while True:
        message = input("> ")
        if message.lower() == "exit":
            break
        sock.sendall(encrypt_message(message, key))

    sock.close()


if __name__ == "__main__":
    start_client()