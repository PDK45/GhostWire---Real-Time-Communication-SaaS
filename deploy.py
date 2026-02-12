import os
import sys
from pyngrok import ngrok
from app import socketio, app

def deploy():
    # check for ngrok auth token
    auth_token = os.environ.get("NGROK_AUTH_TOKEN")
    if auth_token:
        ngrok.set_auth_token(auth_token)
    else:
        print("WARNING: NGROK_AUTH_TOKEN not set. Session may be limited.")

    # Open a Ngrok tunnel to the socketio port
    public_url = ngrok.connect(5000).public_url
    print(f" * Public URL: {public_url}")
    print(f" * Access this URL from any device (Smartphone/Tablet/PC)")

    # Update app config if needed (e.g., for CORS, though we set it to *)
    
    print("Starting GhostWire Secure Server...")
    # Using the same startup logic as app.py but wrapping it
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)

if __name__ == "__main__":
    deploy()
