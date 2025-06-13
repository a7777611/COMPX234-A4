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

def download_file(sock, server_addr, filename):
    # 发送DOWNLOAD请求
    response = send_and_receive(sock, f"DOWNLOAD {filename}", server_addr)

    if response.startswith("ERR"):
        print(f"Error: {response}")
        return
    
    #解析OK响应
    parts = response.split()
    filesize = int(parts[4])
    port = int(parts[6])
    print(f"Downloading {filename} (size: {filesize} bytes)")

    #连接新端口
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_file_addr = (server_addr[0], port)

    #分块下载
    if not os.path.exists("Client"):
        os.makedirs("Client")
    with open(f"Client/{filename}", 'wb') as f:
        start = 0
        while start < filesize:
            end = min(start + 999, filesize - 1)
            request = f"FILE {filename} GET START {start} END {end}"
            response = send_and_receive(client_sock, request, server_file_addr)
            
            if "OK" in response:
                data_part = response.split("DATA ")[1]
                decoded = base64.b64decode(data_part.encode())
                f.write(decoded)
                print("*", end="", flush=True)
                start = end + 1
    
    #关闭连接
    send_and_receive(client_sock, f"FILE {filename} CLOSE", server_file_addr)
    print(f"\nDownloaded: {filename}")



def main():
    host = input("Enter server host: ")
    port = int(input("Enter server port: "))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        msg = input("Enter message: ")
        sock.sendto(msg.encode(), (host, port))

if __name__ == "__main__":
    main()
