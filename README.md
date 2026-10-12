# Encrypted Chat App

A multi-client TCP chat application with AES encryption, built in Python as part of my Syntecxhub Cybersecurity internship (Week 2 task).

## What it does
A server/client chat system where every message is encrypted with AES before it leaves the client and decrypted only on arrival. The server can handle multiple clients at once, broadcasting messages between them, and logs all chat activity to a file.

## Features
- Client/server architecture over TCP sockets
- AES-CBC encryption applied to every message, both directions
- A fresh random IV generated for every single message (no IV reuse)
- Pre-shared key handling — both client and server derive the same AES key from a shared passphrase using PBKDF2
- Supports multiple clients connected at the same time, each handled on its own thread
- Nickname-based messages, broadcast to all other connected clients
- Message logging to `chat_log.txt`
- Clean handling of client disconnects (server doesn't crash when someone leaves)

## Technologies used
- Python 3
- `socket` - TCP client/server communication
- `threading` - handling multiple clients concurrently, and listening for messages on the client while still being able to type
- `cryptography` - AES-CBC encryption, PBKDF2 key derivation, PKCS7 padding
- `logging` - persistent chat history

## How it works
Both the client and server derive the same AES key from a shared passphrase using PBKDF2 (so the raw passphrase itself is never used directly as the key). When a client sends a message, it's padded to fit AES's block size, encrypted with a brand new random IV, and the IV is sent along with the ciphertext (the IV doesn't need to be secret - it just has to be unique per message, which is what actually keeps the encryption secure). The server receives the message, decrypts it using the shared key, logs it, then re-encrypts it (again with a new IV) before broadcasting it out to every other connected client. Each client runs a background thread so it can listen for incoming messages while the user is still free to type and send their own.

## How to run
Install the one dependency:
```bash
pip install cryptography
```

Start the server first:
```bash
python chat_server.py
```

Then start one or more clients, each in its own terminal:
```bash
python chat_client.py
```
Enter a nickname when prompted, then start typing messages. Type `exit` to disconnect.

## Security considerations
- The pre-shared passphrase is hardcoded in this version for simplicity - in a real-world system this would need a proper key exchange mechanism (like Diffie-Hellman) instead of a passphrase both sides already have to know in advance.
- IV reuse is one of the most common real-world mistakes in AES-CBC implementations - reusing the same IV across messages can leak information about the plaintext. This project generates a new random IV for every message specifically to avoid that.
- There's no authentication of client identity beyond a self-chosen nickname - anyone who knows the passphrase and server address can connect and claim any nickname.
- Traffic is encrypted, but the server itself can see all plaintext messages (it has to, in order to broadcast them) - this isn't end-to-end encryption, more like encryption-in-transit with a trusted server in the middle.

## Limitations
- No real key exchange protocol - relies on a pre-shared passphrase
- No user authentication - nicknames aren't verified or unique-checked
- No message persistence beyond the log file (no chat history replay for clients joining late)
- Server can read all messages in plaintext (not end-to-end encrypted)

## Future improvements
- Implement a real key exchange (e.g., Diffie-Hellman) instead of a pre-shared passphrase
- Add basic authentication so nicknames can't be spoofed
- Add true end-to-end encryption so even the server can't read message contents
- Add a simple GUI instead of a terminal-only interface

## Real-world relevance
Encryption in transit is the foundation behind basically every secure communication system in use today - HTTPS, messaging apps, VPNs. This project builds that concept from scratch: encrypting before sending, decrypting only at the destination, and handling IVs correctly, which is a detail that's genuinely easy to get wrong and has caused real vulnerabilities in production systems. Being able to recognize encrypted vs. plaintext traffic, and understanding what "done correctly" looks like, is useful context for reviewing network traffic in a SOC environment - even though building the encryption itself isn't typically an L1 analyst task.