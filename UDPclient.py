import socket
import base64
import os
import time

def send_and_receive(sock, msg, addr, max_retries=5):
    print(f"Sending: {msg} to {addr}")  # 添加发送日志
    for attempt in range(max_retries):
        #print(f"尝试 {attempt+1}/{max_retries}")
        sock.sendto(msg.encode(), addr)
        sock.settimeout(2 + attempt * 2) #Dynamic timeout
        try:
            #print("等待服务器响应...")
            data, _ = sock.recvfrom(2048)
            #print(f"Received: {data.decode()}")  # 添加接收日志
            return data.decode()
        except socket.timeout:
            print(f"Timeout, retrying...({attempt + 1}/{max_retries})")
        except ConnectionResetError:
            print("Connection was reset by server")  # 专门处理连接重置
            time.sleep(1)  # 等待1秒再重试
    raise Exception("Max retries exceeded")

def download_file(sock, server_addr, filename):
    # Send a DOWNLOAD request
    response = send_and_receive(sock, f"DOWNLOAD {filename}", server_addr)

    if response.startswith("ERR"):
        print(f"Error: {response}")
        return
    
    #Analyze OK response
    parts = response.split()
    if len(parts) < 6 or parts[0] != "OK" or parts[2] != "SIZE" or parts[4] != "PORT":
            raise ValueError("Invalid server response format")
    filesize = int(parts[3])
    port = int(parts[5])
    print(f"Downloading {filename} (size: {filesize} bytes)")

    #Connect to new port
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_file_addr = (server_addr[0], port)

    #Block Download
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
    
    #close connect
    send_and_receive(client_sock, f"FILE {filename} CLOSE", server_file_addr)
    print(f"\nDownloaded: {filename}")



def main():
    host = input("Enter server host: ")
    port = int(input("Enter server port: "))
    filelist = input("Enter file list: ")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_addr = (host, port)

    with open(filelist, 'r') as f:
        for line in f:
            filename = line.strip()
            if filename:  # skip blank lines
                download_file(sock, server_addr, filename)


if __name__ == "__main__":
    main()
