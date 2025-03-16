import socket
import threading

class IoTDeviceFirewall:
    def __init__(self):
        self.allowed_ips = set()  # Set of allowed IP addresses
        self.blocked_ips = set()  # Set of blocked IP addresses
        self.server_socket = None
        self.is_running = False

    def block_ip(self, ip):
        """Block a specific IP address."""
        if self.validate_ip(ip):
            self.blocked_ips.add(ip)
            print(f"Blocked IP: {ip}")
        else:
            print(f"Invalid IP address: {ip}")

    def allow_ip(self, ip):
        """Allow a specific IP address."""
        if self.validate_ip(ip):
            self.blocked_ips.discard(ip)
            self.allowed_ips.add(ip)
            print(f"Allowed IP: {ip}")
        else:
            print(f"Invalid IP address: {ip}")

    def validate_ip(self, ip):
        """Validate an IP address."""
        try:
            socket.inet_aton(ip)
            return True
        except socket.error:
            return False

    def is_allowed(self, ip):
        """Check if an IP address is allowed."""
        return ip not in self.blocked_ips

    def start(self, host='0.0.0.0', port=8080):
        """Start the firewall."""
        self.is_running = True
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((host, port))
            self.server_socket.listen(5)
            print(f"Firewall is running on {host}:{port}...")

            while self.is_running:
                client_socket, addr = self.server_socket.accept()
                ip = addr[0]
                print(f"Connection attempt from {ip}")

                if not self.is_allowed(ip):
                    print(f"Blocked connection from {ip}")
                    client_socket.close()
                else:
                    print(f"Allowed connection from {ip}")
                    threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()

    def stop(self):
        """Stop the firewall."""
        self.is_running = False
        if self.server_socket:
            self.server_socket.close()
        print("Firewall stopped.")

    def handle_client(self, client_socket):
        """Handle a client connection."""
        try:
            request = client_socket.recv(1024)
            print(f"Received: {request}")
            client_socket.send(b'HTTP/1.1 200 OK\r\n\r\n')
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()

def main():
    firewall = IoTDeviceFirewall()

    # Start the firewall in a separate thread
    firewall_thread = threading.Thread(target=firewall.start, daemon=True)
    firewall_thread.start()

    while True:
        print("\n1. Block IP")
        print("2. Allow IP")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            ip = input("Enter the IP address to block: ")
            firewall.block_ip(ip)
        elif choice == '2':
            ip = input("Enter the IP address to allow: ")
            firewall.allow_ip(ip)
        elif choice == '3':
            firewall.stop()
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()