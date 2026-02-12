import os
import sys
from pyngrok import ngrok
from app import socketio, app

def deploy():
    # Set auth token directly
    ngrok.set_auth_token("388sh3RhhncHugGYnKVPdUYXBee_75aFDxk51fsytxByCec7q")

    # Open a Ngrok tunnel to the socketio port
    public_url = ngrok.connect(5000).public_url
    print(f" * Public URL: {public_url}")
    print(f" * Access this URL from any device (Smartphone/Tablet/PC)")

    # Update app config if needed (e.g., for CORS, though we set it to *)
    
    print("Starting GhostWire Secure Server...")
    # Disable reloader to prevent spawning a child process that tries to open a second tunnel
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True, use_reloader=False)

if __name__ == "__main__":
    deploy()
