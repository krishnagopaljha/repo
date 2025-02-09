import zmq

class SecureServer:
    def __init__(self, bind_address="tcp://192.168.202.231:5555"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.ROUTER)
        self.socket.bind(bind_address)

        self.clients = {}  # Maps {client_id: zmq_identity}
        self.client_id_counter = 1  # Unique numeric Client IDs
        print(f"✅ Secure Server started at {bind_address}")

    def run(self):
        """Main server loop to handle clients."""
        while True:
            message_parts = self.socket.recv_multipart()
            client_identity = message_parts[0]  # ZMQ identity

            if len(message_parts) == 2 and message_parts[1] == b"REGISTER":
                self.register_client(client_identity)
            elif len(message_parts) == 2 and message_parts[1].startswith(b"CONNECT|"):
                self.handle_connection_request(client_identity, message_parts[1])
            elif len(message_parts) == 2:
                self.forward_message(client_identity, message_parts[1])

    def register_client(self, client_identity):
        """Assigns a unique numeric ID to each client."""
        client_id = str(self.client_id_counter)
        self.clients[client_id] = client_identity
        self.client_id_counter += 1

        print(f"✅ Registered Client-{client_id}")
        self.socket.send_multipart([client_identity, f"REGISTERED|{client_id}".encode()])

    def handle_connection_request(self, client_identity, request):
        """Handles client connection requests by verifying IDs."""
        requested_id = request.split(b"|")[1].decode()

        if requested_id in self.clients:
            self.socket.send_multipart([client_identity, b"CONNECTED"])
            print(f"🔗 Client-{requested_id} is now connected.")
        else:
            self.socket.send_multipart([client_identity, b"INVALID_ID"])
            print(f"❌ Connection failed. Client-{requested_id} not found.")

    def forward_message(self, sender_identity, message):
        """Relays messages between clients based on numeric IDs."""
        try:
            sender_id, recipient_id, msg = message.decode().split("|", 2)

            if recipient_id in self.clients:
                recipient_identity = self.clients[recipient_id]
                self.socket.send_multipart([recipient_identity, f"{sender_id}|{msg}".encode()])
                print(f"📩 Message relayed from Client-{sender_id} to Client-{recipient_id}")
            else:
                print(f"⚠ Client-{recipient_id} not found. Message dropped.")
        except Exception as e:
            print(f"⚠ Error forwarding message: {e}")

if __name__ == "__main__":
    server = SecureServer()
    server.run()
