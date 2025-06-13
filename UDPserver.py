import socket
import threading

def main():
    port = int(input("Enter server port: "))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind('0.0.0.0', port)
    print(f"Server running on port {port}...")

    while True:
        data, addr = sock.recvfrom(1024)
        print(f"Received:{data.decode()} from {addr}")

if __name__ == "__main__":
    main()