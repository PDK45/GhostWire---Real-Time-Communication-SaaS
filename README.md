# GhostWire: Real-Time Steganographic SaaS

**GhostWire** is a military-grade secure communication platform that hides encrypted messages within images (Steganography) and self-destructs evidence.

## Features
*   **Real-Time Messaging**: Built on Flask-SocketIO.
*   **Steganography**: Hide text inside images using LSB modification.
*   **AES-256 Encryption**: Messages are encrypted with a user-defined passphrase.
*   **Self-Destruct**: Messages vanish after 30 seconds.
*   **Flash Protocol**: Hover-to-read messages for anti-shoulder-surfing privacy.
*   **PWA**: Installable on mobile/desktop.

## Deployment
1.  **Clone the Repo**:
    ```bash
    git clone https://github.com/PDK45/GhostWire---Real-Time-Communication-SaaS.git
    ```
2.  **Install Requirements**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run**:
    ```bash
    python3 deploy.py
    ```

---
**By Dharani Krishna**
