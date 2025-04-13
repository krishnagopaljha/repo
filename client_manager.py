# client_manager.py

import time

clients = {}

def register_client(name, sid):
    from uuid import uuid4
    client_id = str(uuid4())[:8]
    clients[client_id] = {'name': name, 'sid': sid, 'last_seen': time.time()}
    return client_id

def remove_client_by_sid(sid):
    for cid, data in list(clients.items()):
        if data['sid'] == sid:
            del clients[cid]
            break

def get_sid_by_id(client_id):
    return clients.get(client_id, {}).get('sid')

def update_heartbeat(sid):
    for cid, data in clients.items():
        if data['sid'] == sid:
            data['last_seen'] = time.time()

def remove_stale_clients(timeout=60):
    now = time.time()
    to_remove = [cid for cid, data in clients.items() if now - data['last_seen'] > timeout]
    for cid in to_remove:
        del clients[cid]

def get_clients():
    return clients
