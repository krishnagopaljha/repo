import zmq
import threading
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

class SecureClient:
    def __init__(self, server_address="tcp://127.0.0.1:5555"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.connect(server_address)
        self.socket.setsockopt(zmq.RCVTIMEO, 5000)  # 5 seconds timeout

        self.client_id = None
        self.encryption_key = None
        self.connected_to = None  # Tracks the client we're connected to
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
        if self.connected_to:
            print(f"❌ You are already connected to Client-{self.connected_to}. Disconnect first.")
            return False

        print(f"\n🔗 Requesting connection with Client-{recipient_id}...")
        self.socket.send_multipart([f"CONNECT|{recipient_id}".encode()])

        try:
            response = self.socket.recv_multipart()
            if response[0] == b"CONNECTED":
                # Generate a new AES key for this session
                self.encryption_key = get_random_bytes(16)
                # Send the encryption key to the recipient
                self.socket.send_multipart([f"KEY|{recipient_id}|{base64.b64encode(self.encryption_key).decode()}".encode()])
                self.connected_to = recipient_id
                print(f"✅ Connected to Client-{recipient_id}. Start chatting!")
                return True
            else:
                print("❌ Connection failed.")
                return False
        except zmq.error.Again:
            print("⏳ Server did not respond. Connection attempt failed.")
            return False

    def handle_connection_request(self, sender_id):
        """Handle incoming connection requests."""
        print(f"\n🔗 Connection request from Client-{sender_id}. Accept? (yes/no): ", end="")
        choice = input().strip().lower()
        if choice == "yes":
            self.socket.send_multipart([f"ACCEPT|{sender_id}".encode()])
            self.connected_to = sender_id
            print(f"✅ Connected to Client-{sender_id}. Start chatting!")
            return True
        else:
            self.socket.send_multipart([f"REJECT|{sender_id}".encode()])
            print(f"❌ Rejected connection request from Client-{sender_id}.")
            return False

    def encrypt_message(self, message):
        """Encrypt the message using AES."""
        cipher = AES.new(self.encryption_key, AES.MODE_EAX)
        nonce = cipher.nonce
        ciphertext, tag = cipher.encrypt_and_digest(message.encode())
        return base64.b64encode(nonce + ciphertext + tag).decode()

    def decrypt_message(self, encrypted_message):
        """Decrypt the message using AES."""
        data = base64.b64decode(encrypted_message)
        nonce = data[:16]
        ciphertext = data[16:-16]
        tag = data[-16:]
        cipher = AES.new(self.encryption_key, AES.MODE_EAX, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext.decode()

    def send_message(self):
        """Interactive message sending loop."""
        while True:
            if not self.connected_to:
                continue  # Wait for a connection

            msg = input("You: ")
            if msg.lower() == "exit":
                print("❌ Chat ended.")
                self.socket.send_multipart([f"DISCONNECT|{self.connected_to}".encode()])
                self.connected_to = None
                break
            encrypted_msg = self.encrypt_message(msg)
            self.socket.send_multipart([f"{self.client_id}|{self.connected_to}|{encrypted_msg}".encode()])

    def receive_messages(self):
        """Continuously receive and display messages in a separate thread."""
        while True:
            try:
                response = self.socket.recv_multipart()
                if not response:
                    continue  # Skip empty responses

                message = response[0].decode()

                if message.startswith("REQUEST|"):
                    # Handle connection request
                    sender_id = message.split("|")[1]
                    self.handle_connection_request(sender_id)
                elif message.startswith("KEY|"):
                    # Received the encryption key from the other client
                    parts = message.split("|")
                    if parts[1] == self.client_id:
                        self.encryption_key = base64.b64decode(parts[2])
                        print("🔑 Encryption key received. Secure communication established.")
                elif message.startswith("DISCONNECT|"):
                    # Handle disconnection
                    self.connected_to = None
                    print("❌ The other client has disconnected.")
                elif "|" in message:
                    # Handle regular messages (sender_id|encrypted_msg)
                    sender_id, encrypted_msg = message.split("|", 1)
                    if self.encryption_key:
                        msg = self.decrypt_message(encrypted_msg)
                        print(f"\n📩 Message from Client-{sender_id}: {msg}\nYou: ", end="")
                    else:
                        print(f"\n⚠ No encryption key. Cannot decrypt message.")
                else:
                    print(f"\n⚠ Unknown message format: {message}")
            except zmq.error.Again:
                continue  # Timeout occurred, but keep listening
            except Exception as e:
                print(f"\n⚠ Error processing message: {e}")

if __name__ == "__main__":
    client = SecureClient()

    # Ask for recipient Client ID after registration
    recipient_id = input("\nEnter recipient's Client ID to connect (or press Enter to wait for incoming requests): ")

    if recipient_id:
        if client.connect_to_client(recipient_id):
            # Start message receiver in a separate thread
            receive_thread = threading.Thread(target=client.receive_messages, daemon=True)
            receive_thread.start()

            # Start interactive chat
            client.send_message()
    else:
        print("⏳ Waiting for incoming connection requests...")
        receive_thread = threading.Thread(target=client.receive_messages, daemon=True)
        receive_thread.start()
        while not client.connected_to:
            pass  # Wait for a connection
        client.send_message()
