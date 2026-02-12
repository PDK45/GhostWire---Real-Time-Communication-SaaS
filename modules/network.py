from flask import request
from flask_socketio import emit, join_room, leave_room, close_room
from modules.security import encrypt_message, decrypt_message, hide_data_in_image, reveal_data_from_image
import os
import secrets
import string
import time
import base64
import uuid
from io import BytesIO
from PIL import Image

# State Management
# rooms = { 'CODE': { 'admin': 'sid', 'members': ['sid'], 'created_at': time } }
rooms = {} 
# user_map = { 'sid': { 'username': 'name', 'room': 'CODE' } }
user_map = {}

def generate_room_code(length=6):
    chars = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(secrets.choice(chars) for _ in range(length))
        if code not in rooms:
            return code

def register_socketio_events(socketio):
    @socketio.on('connect')
    def handle_connect():
        print(f"Client connected: {request.sid}")
        # Send initial status but don't auto-join a room yet
        emit('server_status', {'msg': 'Connected to GhostWire Node. Authenticate or Initialize Frequency.', 'sid': request.sid})

    @socketio.on('disconnect')
    def handle_disconnect():
        print(f"Client disconnected: {request.sid}")
        user = user_map.get(request.sid)
        if user:
            room_code = user['room']
            leave_room(room_code)
            
            # Clean up room if empty or if admin left? 
            # For now, let's just remove user from room list
            if room_code in rooms:
                if request.sid in rooms[room_code]['members']:
                    rooms[room_code]['members'].remove(request.sid)
                
                # Notify others
                emit('status', {'msg': f"{user['username']} signal lost."}, room=room_code)
                
                # Update user list for remaining members
                emit_user_list(room_code)
            
            del user_map[request.sid]

    @socketio.on('create_server')
    def handle_create_server(data):
        username = data.get('username', 'Ghost')
        room_code = generate_room_code()
        
        # Initialize Room
        rooms[room_code] = {
            'admin': request.sid,
            'members': [request.sid],
            'created_at': time.time()
        }
        
        # Update User Map
        user_map[request.sid] = {'username': username, 'room': room_code}
        
        join_room(room_code)
        
        emit('server_created', {'code': room_code, 'admin': True})
        emit('status', {'msg': f"Secure Node {room_code} Initialized by ADMIN {username}."}, room=room_code)
        emit_user_list(room_code)

    @socketio.on('join_server')
    def handle_join_server(data):
        username = data.get('username', 'Ghost')
        room_code = data.get('code', '').upper()
        
        if room_code in rooms:
            # Join Room
            rooms[room_code]['members'].append(request.sid)
            user_map[request.sid] = {'username': username, 'room': room_code}
            
            join_room(room_code)
            
            is_admin = (rooms[room_code]['admin'] == request.sid) 
            
            emit('server_joined', {'code': room_code, 'admin': is_admin})
            emit('status', {'msg': f"{username} has uplinked to the node."}, room=room_code)
            emit_user_list(room_code)
        else:
            emit('error', {'msg': 'Invalid Frequency Code. Access Denied.'})

    @socketio.on('kick_user')
    def handle_kick_user(data):
        target_sid = data.get('target_sid')
        # Check if requester is admin of their room
        requester_info = user_map.get(request.sid)
        if not requester_info: return
        
        room_code = requester_info['room']
        if rooms[room_code]['admin'] == request.sid:
            if target_sid in rooms[room_code]['members'] and target_sid != request.sid:
                 # Emit event to target to force reload or show kicked message
                 emit('kicked', {'msg': 'You have been disconnected by the Administrator.'}, room=target_sid)
        else:
            emit('error', {'msg': 'Unauthorized. Admin access required.'})

    @socketio.on('message')
    def handle_message(data):
        """Handle standard text messages."""
        user = user_map.get(request.sid)
        if user:
            room_code = user['room']
            emit('message', {
                'username': user['username'],
                'msg': data.get('msg'), 
                'timestamp': time.strftime("%H:%M")
            }, room=room_code)

    @socketio.on('secure_image')
    def handle_secure_image(data):
        """
        Handle image upload with hidden data + passphrase + self-destruct.
        """
        user = user_map.get(request.sid)
        if not user: return
        
        room_code = user['room']
        secret_text = data.get('secret_text')
        passphrase = data.get('passphrase')
        image_data = data.get('image')
        is_self_destruct = data.get('is_self_destruct', False)
        
        if not passphrase:
            emit('error', {'msg': 'Encryption Passphrase Required for Secure Transmission.'})
            return

        try:
            # 1. Encrypt with User Passphrase
            encrypted_payload = encrypt_message(secret_text, passphrase)
            
            # 2. Process Image
            if 'base64,' in image_data:
                header, encoded = image_data.split('base64,', 1)
                image_data = encoded
            
            img_bytes = base64.b64decode(image_data)
            img = Image.open(BytesIO(img_bytes))
            
            temp_filename = f"temp_{secrets.token_hex(4)}.png"
            temp_path = os.path.join('static', 'images', temp_filename)
            img.save(temp_path)
            
            # 3. Hide Encrypted Payload
            secret_img = hide_data_in_image(temp_path, encrypted_payload)
            
            # Generate Unique ID for the artifact
            artifact_id = str(uuid.uuid4())
            secure_filename = f"ghost_{artifact_id}.png"
            secure_path = os.path.join('static', 'images', secure_filename)
            secret_img.save(secure_path)
            
            os.remove(temp_path)
            
            image_url = f"/static/images/{secure_filename}"
            emit('ghost_image', {
                'id': artifact_id,
                'url': image_url, 
                'username': user['username'],
                'timestamp': time.strftime("%H:%M"),
                'is_self_destruct': is_self_destruct
            }, room=room_code)
            
        except Exception as e:
            print(f"Error processing secure image: {e}")
            emit('error', {'msg': 'Failed to process secure transmission.'})

    @socketio.on('delete_artifact')
    def handle_delete_artifact(data):
        """
        Handle self-destruct request.
        """
        artifact_id = data.get('id')
        user = user_map.get(request.sid)
        if not user: return

        room_code = user['room']
        
        # Verify filename matches ID pattern to prevent directory traversal or arbitrary deletion
        filename = f"ghost_{artifact_id}.png"
        filepath = os.path.join('static', 'images', filename)
        
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"Artifact {filename} self-destructed.")
                emit('remove_node', {'id': artifact_id}, room=room_code)
                emit('status', {'msg': f"SECURE ARTIFACT {artifact_id[-4:]} HAS BEEN PURGED."}, room=room_code)
            except Exception as e:
                print(f"Error deleting artifact: {e}")
        else:
            print(f"Artifact {filename} not found for deletion.")

    @socketio.on('decrypt_request')
    def handle_decrypt_request(data):
        """
        Decrypt data utilizing user provided passphrase.
        """
        image_url = data.get('url')
        passphrase = data.get('passphrase')
        
        if not passphrase:
            emit('decryption_result', {'message': "Passphrase required.", 'error': True})
            return

        if image_url.startswith('/'):
            image_url = image_url[1:]
        
        try:
            encrypted_data = reveal_data_from_image(image_url)
            if encrypted_data:
                # Decrypt with passphrase
                decrypted_msg = decrypt_message(encrypted_data, passphrase)
                if decrypted_msg:
                    emit('decryption_result', {'message': decrypted_msg, 'url': data.get('url')})
                else:
                    emit('decryption_result', {'message': "Decryption Failed. Invalid Passphrase.", 'error': True})
            else:
                emit('decryption_result', {'message': "No ghost data found.", 'error': True})
        except Exception as e:
            print(f"Decryption failed: {e}")
            emit('decryption_result', {'message': "System Error during decryption.", 'error': True})

def emit_user_list(room_code):
    if room_code in rooms:
        member_list = []
        admin_sid = rooms[room_code]['admin']
        for sid in rooms[room_code]['members']:
            u = user_map.get(sid)
            if u:
                member_list.append({
                    'username': u['username'],
                    'sid': sid,
                    'is_admin': (sid == admin_sid)
                })
        emit('user_list', {'users': member_list}, room=room_code)
