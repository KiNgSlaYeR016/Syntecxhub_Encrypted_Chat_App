# Encrypted chat server
# Accepts multiple clients over TCP, decrypts incoming messages, broadcasts them
# (re-encrypted) to everyone else connected. Every message uses a fresh random IV.

import socket
import threading
import logging
from datetime import datetime
from crypto_utils import encrypt_message, decrypt_message, derive_key

HOST = "0.0.0.0"   # listen on all interfaces
PORT = 5050
PRE_SHARED_PASSPHRASE = "syntecxhub-week2"  # both client and server must use the same one

logging.basicConfig(
    filename="chat_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

clients = {}          # socket -> nickname
clients_lock = threading.Lock()

key, salt = derive_key(PRE_SHARED_PASSPHRASE)  # same passphrase+salt must match on client side


def broadcast(sender_sock, plaintext):
    # sends the message to everyone except whoever sent it
    with clients_lock:
        nickname = clients.get(sender_sock, "unknown")
        full_message = f"{nickname}: {plaintext}"
        logging.info(full_message)

        for client_sock in list(clients.keys()):
            if client_sock == sender_sock:
                continue
            try:
                packet = encrypt_message(full_message, key)
                client_sock.sendall(packet)
            except Exception:
                remove_client(client_sock)


def remove_client(sock):
    with clients_lock:
        nickname = clients.pop(sock, "unknown")
    try:
        sock.close()
    except Exception:
        pass
    print(f"[-] {nickname} disconnected")
    logging.info(f"{nickname} disconnected")


def handle_client(sock, addr):
    try:
        # first message from a client is treated as their nickname (sent encrypted too)
        raw = sock.recv(4096)
        nickname = decrypt_message(raw, key)

        with clients_lock:
            clients[sock] = nickname

        print(f"[+] {nickname} connected from {addr}")
        logging.info(f"{nickname} connected from {addr}")

        while True:
            raw = sock.recv(4096)
            if not raw:
                break  # client closed the connection

            plaintext = decrypt_message(raw, key)
            print(f"{nickname}: {plaintext}")
            broadcast(sock, plaintext)

    except Exception as e:
        print(f"Error with {addr}: {e}")
    finally:
        remove_client(sock)


def start_server():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((HOST, PORT))
    server_sock.listen()

    print(f"Server listening on {HOST}:{PORT}")
    logging.info("--- Server started ---")

    while True:
        client_sock, addr = server_sock.accept()
        t = threading.Thread(target=handle_client, args=(client_sock, addr), daemon=True)
        t.start()


if __name__ == "__main__":
    start_server()