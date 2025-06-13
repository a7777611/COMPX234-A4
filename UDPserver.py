import socket
import threading
import random
import os
import base64

class FileServerThread(threading.Thread):
    def __init__(self, client_addr, filename):
        threading.Thread.__init__(self)
        self.client_addr = client_addr
        self.filename = filename
        self.port = random.randint(50000,51000)
        self.filepath = os.path.join("Server", filename)

    def run(self):
        try:
            # creat a new socket to handle file transport
            sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            sock.bind(('0.0.0.0', self.port))
            # check file wether exist
            if not os.path.exists(self.filepath):
                sock.sendto(f"ERR {self.filename} NOT_FOUND".encode(), self.client_addr)
                return
            
            #发送ok响应
            filesize = os.path.exists(self.filepath)
            sock.sendto(f"OK {self.filename} SIZE {filesize} PORT {self.port}".encode(), self.client_addr)
            
            #处理文件块请求
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

        finally:
            sock.close()
    

def main():
    if not os.path.exists("Server"):
        os.makedirs("Server")
    
    port = int(input("Enter server port: "))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind('0.0.0.0', port)
    print(f"Server running on port {port}...")

    while True:
        data, addr = sock.recvfrom(1024)
        if data.decode().startswith("DOWNLOAD"):
            filename = data.decode().split()[1]
            thread = FileServerThread(addr, filename, port)
            thread.start()
        

if __name__ == "__main__":
    main()