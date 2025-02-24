import zmq

class SecureServer:
    def __init__(self, bind_address="tcp://127.0.0.1:5555"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.ROUTER)
        self.socket.bind(bind_address)

        self.clients = {}  # Maps {client_id: zmq_identity}
        self.connections = {}  # Maps {client_id: connected_to}
        self.client_id_counter = 1  # Unique numeric Client IDs
        print(f"✅ Secure Server started at {bind_address}")

    def run(self):
        """Main server loop to handle clients."""
        while True:
            try:
                message_parts = self.socket.recv_multipart()
                client_identity = message_parts[0]  # ZMQ identity

                if len(message_parts) == 2:
                    message = message_parts[1].decode()
                    if message == "REGISTER":
                        self.register_client(client_identity)
                    elif message.startswith("CONNECT|"):
                        self.handle_connection_request(client_identity, message)
                    elif message.startswith("ACCEPT|"):
                        self.handle_connection_accept(client_identity, message)
                    elif message.startswith("REJECT|"):
                        self.handle_connection_reject(client_identity, message)
                    elif message.startswith("DISCONNECT|"):
                        self.handle_disconnect(client_identity, message)
                    elif message.startswith("KEY|"):
                        self.forward_key(client_identity, message)
                    else:
                        self.forward_message(client_identity, message_parts[1])
            except Exception as e:
                print(f"⚠ Error processing message: {e}")

    def register_client(self, client_identity):
        """Assigns a unique numeric ID to each client."""
        client_id = str(self.client_id_counter)
        self.clients[client_id] = client_identity
        self.client_id_counter += 1

        print(f"✅ Registered Client-{client_id}")
        self.socket.send_multipart([client_identity, f"REGISTERED|{client_id}".encode()])

    def handle_connection_request(self, client_identity, request):
        """Handles client connection requests by verifying IDs."""
        requested_id = request.split("|")[1]
        sender_id = self.get_client_id(client_identity)

        if requested_id in self.clients and sender_id not in self.connections:
            # Forward the request to the recipient
            recipient_identity = self.clients[requested_id]
            self.socket.send_multipart([recipient_identity, f"REQUEST|{sender_id}".encode()])
            print(f"🔗 Connection request forwarded from Client-{sender_id} to Client-{requested_id}")
        else:
            self.socket.send_multipart([client_identity, b"INVALID_ID"])
            print(f"❌ Connection failed. Client-{requested_id} not found or sender is already connected.")

    def handle_connection_accept(self, client_identity, message):
        """Handles connection acceptance."""
        sender_id = message.split("|")[1]
        recipient_id = self.get_client_id(client_identity)

        # Establish the connection
        self.connections[sender_id] = recipient_id
        self.connections[recipient_id] = sender_id

        # Notify both clients
        self.socket.send_multipart([self.clients[sender_id], b"CONNECTED"])
        self.socket.send_multipart([client_identity, b"CONNECTED"])
        print(f"🔗 Client-{sender_id} and Client-{recipient_id} are now connected.")

    def handle_connection_reject(self, client_identity, message):
        """Handles connection rejection."""
        sender_id = message.split("|")[1]
        self.socket.send_multipart([self.clients[sender_id], b"REJECTED"])
        print(f"❌ Client-{self.get_client_id(client_identity)} rejected connection request from Client-{sender_id}.")

    def handle_disconnect(self, client_identity, message):
        """Handles disconnection."""
        sender_id = self.get_client_id(client_identity)
        if sender_id in self.connections:
            recipient_id = self.connections[sender_id]
            del self.connections[sender_id]
            del self.connections[recipient_id]
            self.socket.send_multipart([self.clients[recipient_id], f"DISCONNECT|{sender_id}".encode()])
            print(f"❌ Client-{sender_id} and Client-{recipient_id} have disconnected.")

    def forward_key(self, client_identity, message):
        """Relays the encryption key to the recipient."""
        parts = message.split("|")
        recipient_id = parts[1]
        key = parts[2]

        if recipient_id in self.clients:
            recipient_identity = self.clients[recipient_id]
            self.socket.send_multipart([recipient_identity, f"KEY|{recipient_id}|{key}".encode()])
            print(f"🔑 Encryption key relayed to Client-{recipient_id}")
        else:
            print(f"⚠ Client-{recipient_id} not found. Key not forwarded.")

    def forward_message(self, client_identity, message):
        """Relays messages between clients based on numeric IDs."""
        try:
            sender_id, recipient_id, msg = message.decode().split("|", 2)

            if recipient_id in self.clients:
                recipient_identity = self.clients[recipient_id]
                # Forward the message in the correct format: sender_id|encrypted_msg
                self.socket.send_multipart([recipient_identity, f"{sender_id}|{msg}".encode()])
                print(f"📩 Message relayed from Client-{sender_id} to Client-{recipient_id}")
            else:
                print(f"⚠ Client-{recipient_id} not found. Message dropped.")
        except Exception as e:
            print(f"⚠ Error forwarding message: {e}")

    def get_client_id(self, client_identity):
        """Returns the client ID for a given ZMQ identity."""
        for client_id, identity in self.clients.items():
            if identity == client_identity:
                return client_id
        return None

if __name__ == "__main__":
    server = SecureServer()
    server.run()
