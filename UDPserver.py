import socket
import threading
import random
import os
import base64

class FileServerThread(threading.Thread):
    def __init__(self, client_addr, filename, server_port):
        threading.Thread.__init__(self)
        self.client_addr = client_addr
        self.filename = filename
        self.server_port = server_port
        self.port = random.randint(50000,51000)
        self.filepath = os.path.join("Server", filename)
        #print(f"新线程: 文件={filename}, 客户端={client_addr}, 服务端口={server_port}, 传输端口={self.port}")

    def run(self):
        try:
            # creat a new socket to handle file transport
            sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            sock.bind(('0.0.0.0', self.port))
            print(f"New thread started for {self.filename} on port {self.port}")  # 添加日志
            # check file wether exist
            if not os.path.exists(self.filepath):
                print(f"File not found: {self.filename}")  # 添加日志
                sock.sendto(f"ERR {self.filename} NOT_FOUND".encode(), self.client_addr)
                return
            
            #Send an OK response
            filesize = os.path.getsize(self.filepath)
            print(f"Sending file info: {self.filename}, size: {filesize}")  # 添加日志
            sock.sendto(f"OK {self.filename} SIZE {filesize} PORT {self.port}".encode(), self.client_addr)
            
            #Process file block requests
            with open(self.filepath, 'rb') as f:
                while True:
                    data, addr = sock.recvfrom(1024)
                    request = data.decode().split()
                    if request[0] == "FILE" and request[2] == "GET":
                        start = int(request[4])
                        end = int(request[6])
                        f.seek(start)
                        chunk = f.read(end - start +1)
                        encode = base64.b64encode(chunk).decode()
                        response = f"FILE {self.filename} OK START {start} END {end} DATA {encode}"
                        sock.sendto(response.encode(), addr)
                    elif request[0] == "FILE" and request[2] == "CLOSE":
                        sock.sendto(f"FILE {self.filename} CLOSE_OK".encode(), addr)

                        break
        except Exception as e:
            print(f"Server thread error: {e}")  # 捕获所有异常
        finally:
            sock.close()
    

def main():
    if not os.path.exists("Server"):
        os.makedirs("Server")
    
    port = int(input("Enter server port: "))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', port))
    print(f"Server running on port {port}...")

    while True:
        #print("等待客户端消息...")
        data, addr = sock.recvfrom(1024)
        #print(f"收到来自 {addr} 的消息: {data.decode()}")
        if data.decode().startswith("DOWNLOAD"):
            filename = data.decode().split()[1]
            #print(f"开始处理 {filename} 请求")
            thread = FileServerThread(addr, filename, port)
            thread.start()
    
        

if __name__ == "__main__":
    main()