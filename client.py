import zmq
import threading

class SecureClient:
    def __init__(self, server_address="tcp://192.168.202.231:5555"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.connect(server_address)
        self.socket.setsockopt(zmq.RCVTIMEO, 5000)  # 5 seconds timeout

        self.client_id = None
        self.register()

    def register(self):
        """Register client and receive a unique numeric Client ID."""
        print("📡 Registering with the server...")
        self.socket.send_multipart([b"REGISTER"])

        try:
            response = self.socket.recv_multipart()
            if response[0].startswith(b"REGISTERED|"):
                self.client_id = response[0].split(b"|")[1].decode()
                print(f"✅ You are registered as Client-{self.client_id}")
            else:
                print("❌ Registration failed.")
        except zmq.error.Again:
            print("⏳ Server did not respond. Check if it's running.")

    def connect_to_client(self, recipient_id):
        """Request connection with another client."""
        print(f"\n🔗 Requesting connection with Client-{recipient_id}...")
        self.socket.send_multipart([f"CONNECT|{recipient_id}".encode()])

        try:
            response = self.socket.recv_multipart()
            if response[0] == b"CONNECTED":
                print(f"✅ Connected to Client-{recipient_id}. Start chatting!")
                return True
            else:
                print("❌ Invalid ID! Connection failed.")
                return False
        except zmq.error.Again:
            print("⏳ Server did not respond. Connection attempt failed.")
            return False

    def send_message(self, recipient_id):
        """Interactive message sending loop."""
        while True:
            msg = input("You: ")
            if msg.lower() == "exit":
                print("❌ Chat ended.")
                break
            self.socket.send_multipart([f"{self.client_id}|{recipient_id}|{msg}".encode()])

    def receive_messages(self):
        """Continuously receive and display messages in a separate thread."""
        while True:
            try:
                response = self.socket.recv_multipart()
                sender_id, msg = response[0].decode().split("|", 1)
                print(f"\n📩 Message from Client-{sender_id}: {msg}\nYou: ", end="")
            except zmq.error.Again:
                continue  # Timeout occurred, but keep listening

if __name__ == "__main__":
    client = SecureClient()

    # Ask for recipient Client ID after registration
    recipient_id = input("\nEnter recipient's Client ID to connect: ")

    if client.connect_to_client(recipient_id):
        # Start message receiver in a separate thread
        receive_thread = threading.Thread(target=client.receive_messages, daemon=True)
        receive_thread.start()

        # Start interactive chat
        client.send_message(recipient_id)
