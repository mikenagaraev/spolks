import socket
import threading
from datetime import datetime
import sys
from commands import server_commands, client_commands, help_list
#
# ip = '127.0.0.1'
# port = 8081

# ip = '192.168.0.110'
ip = ''
port = 9001

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((ip, port))
server.listen(5)


def show_start_message():
    print("Hello, listened on %s:%d" %(ip, port))
    show_server_menu()


def handle_client(client_socket):
    while True:
        request = client_socket.recv(2048).decode('utf-8')
        print("[*] Received: %s" %request)
        handle_client_request(client_socket, request)
        client_socket.shutdown(socket.SHUT_WR)

def handle_client_request(client, request):
    command = request.split()
    name_command = command[0]
    if (len(command) == 2):
        body = command[1]
    else:
        body = ""

    if (client_commands.get(name_command) == "download"):
        check_existing_file(body)
        download(body)
    if (client_commands.get(name_command) == "delete"):
        check_existing_file(body)
        delete(body)
    if (client_commands.get(name_command) == "upload"):
        check_existing_file(body)
        upload(body)

def check_existing_file(file_name):
    pass

def delete(file_name):
    pass

def upload(file_name):
    f = open(file_name, 'wb')
    data = client.recv(1024)
    while (data):
        f.write(data)
        data = client.recv(1024)
    f.close()


def download(file_name):
    f = open (file_name, "rb")
    data_file = f.read(1024)
    while (data_file):
        client.send(data_file)
        data_file = f.read(1024)

    f.close()

def server_cli():
    while True:
        command = input_command()
        command, body = parse_server_command(command)
        handle_server_command(command, body)

def parse_server_command(command):
    command = command.split()
    name_command = command[0]
    if (len(command) == 2):
        body = command[1]
    else:
        body = ""
    return [name_command, body]

def handle_server_command(command, body):
    if (server_commands.get(command) == "help"):
        show_server_menu()
    if (server_commands.get(command) == "echo"):
        print(body)
    if (server_commands.get(command) == "time"):
        print("Server time: " + str(datetime.now()))
    if (server_commands.get(command) == "exit"):
        server.close()
        sys.exit()


def input_command():
    return raw_input("")

def show_server_menu():
    for x in help_list:
        print x, ": ", help_list[x]


show_start_message();
server_cli = threading.Thread(target=server_cli)
server_cli.start()



while True:
    client, addr = server.accept()
    print("[*] Accepted connection from: %s:%d" % (addr[0], addr[1]))

    client_handle = threading.Thread(target=handle_client, args=(client,))
    client_handle.start()
