from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import random
import string
import time
import socket

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

clients = {}

def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('register')
def handle_register(data):
    name = data.get('name', '').strip()
    if not name or len(name) > 30:
        emit('error', {'message': 'Invalid name.'})
        return

    user_id = generate_id()
    while user_id in clients:
        user_id = generate_id()

    clients[user_id] = {
        'name': name,
        'sid': request.sid,
        'last_seen': time.time()
    }

    emit('registered', {'id': user_id})
    print(f"User registered: {name} ({user_id})")

@socketio.on('signal')
def handle_signal(data):
    from_id = data.get('from')
    target_id = data.get('target')
    signal = data.get('signal')

    if not all([from_id, target_id, signal]):
        return

    target = clients.get(target_id)
    if target:
        emit('signal', {
            'from': from_id,
            'signal': signal
        }, room=target['sid'])
    else:
        emit('error', {'message': 'Target not found.'})

@socketio.on('get_peer_name')
def get_peer_name(data):
    target_id = data.get('target')
    if target_id in clients:
        name = clients[target_id]['name']
        emit('peer_name', {'name': name}, room=request.sid)

@socketio.on('heartbeat')
def heartbeat():
    for uid, info in list(clients.items()):
        if info['sid'] == request.sid:
            clients[uid]['last_seen'] = time.time()

@socketio.on('disconnect')
def handle_disconnect():
    to_remove = None
    for uid, info in clients.items():
        if info['sid'] == request.sid:
            to_remove = uid
            break
    if to_remove:
        print(f"User disconnected: {clients[to_remove]['name']} ({to_remove})")
        del clients[to_remove]

def get_local_ip():
    """Get the LAN IP of the machine."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Use Google DNS to get local IP
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

if __name__ == '__main__':
    local_ip = get_local_ip()
    port = 5000
    print(f"\nServer running!")
    print(f"Local:   http://127.0.0.1:{port}")
    print(f"Network: http://{local_ip}:{port}\n")
    socketio.run(app, host='0.0.0.0', port=port)
