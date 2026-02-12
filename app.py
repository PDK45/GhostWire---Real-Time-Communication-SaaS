from flask import Flask, render_template
from flask_socketio import SocketIO
from modules.network import register_socketio_events
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'ghostwire-dev-secret')
app.config['DEBUG'] = True

# Initialize SocketIO
# allow_unsafe_werkzeug=True is needed for dev environment if using Werkzeug
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading') 

# Register Events
register_socketio_events(socketio)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    print("Starting GhostWire Secure Server...")
    print(f"Access on http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
