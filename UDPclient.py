import socket

def main():
    host = input("Enter server host: ")
    port = int(input("Enter server port: "))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        msg = input("Enter message: ")
        sock.sendto(msg.encode(), (host, port))

if __name__ == "__main__":
    main()
