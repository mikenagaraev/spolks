import socket
import threading
from commands import server_commands, client_commands
#
# ip = '127.0.0.1'
# port = 8081

ip = '192.168.0.110'
port = 9001

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((ip, port))
server.listen(1)


def show_start_message():
    print("Hello, listened on %s:%d" %(ip, port))

def handle_client(client_socket):
    while True:
        request = client_socket.recv(2048).decode('utf-8')
        print("[*] Received: %s" %request)
        handle_client_request(client_socket, request)
        client_socket.shutdown(socket.SHUT_WR)

def handle_client_request(client, request):
    command, body = request.split(":")
    if (client_commands.get(command) == "download"):
        download(body)
    if (client_commands.get(command) == "delete"):
        delete(body)
    if (client_commands.get(command) == "upload"):
        upload(body)

def delete(file_name):
    pass

def upload(file_name):
    pass


def download(file_name):
    f = open (file_name, "rb")
    data_file = f.read(1024)
    while (data_file):
        client.send(data_file)
        data_file = f.read(1024)

    f.close()


show_start_message();

while True:
    client, addr = server.accept()
    print("[*] Accepted connection from: %s:%d" % (addr[0], addr[1]))

    client_handle = threading.Thread(target=handle_client, args=(client,))
    client_handle.start()
