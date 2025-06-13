import socket
import base64
import os
import time

def send_and_receive(sock, msg, addr, max_retries=5):
    for attempt in range(max_retries):
        sock.sendto(msg.encode(), addr)
        sock.settimeout(2 + attempt * 2) #动态超时
        try:
            data, _ = sock.recvform(2048)
            return data.decode()
        except socket.timeout:
            print(f"Timeout, retrying...({attempt + 1}/{max_retries})")
    raise Exception("Max retries exceeded")


def main():
    host = input("Enter server host: ")
    port = int(input("Enter server port: "))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        msg = input("Enter message: ")
        sock.sendto(msg.encode(), (host, port))

if __name__ == "__main__":
    main()
