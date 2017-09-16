import socket
import threading
from datetime import datetime
import sys
import os
import os.path
from commands import server_commands, client_commands, help_list
#
ip = '192.168.100.7'
# port = 8081

# ip = '192.168.0.110'

port = 9001
BUFFER_SIZE = 2048


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((ip, port))
server.listen(5)


def show_start_message():
    print("Hello, listened on %s:%d" %(ip, port))
    show_server_menu()


def handle_client(client_socket):
    while True:
        request = client_socket.recv(BUFFER_SIZE).decode('utf-8')
        request = request.strip()
        print("[*] Received: %s" %request)
        handle_client_request(client_socket, request)
        # client_socket.shutdown(socket.SHUT_WR)

def handle_client_request(client, request):
    command = request.split()
    name_command = command[0]

    if (len(command) == 2):
        file_name = command[1]

    if (client_commands.get(name_command) == "download"):
        if (is_file_exist(file_name)):
            send_status(client, name_command, 200)
            download(file_name)
        else:
            no_file = "File: " + file_name + " is not exist."
            send_status_and_message(client, name_command, 500, "No such file")

    elif (client_commands.get(name_command) == "delete"):
        if (is_file_exist(file_name)):
            send_status(client, name_command, 200)
            delete(file_name)
        else:
            no_file = "File: " + file_name + " is not exist."
            send_status_and_message(client, name_command, 500, "No such file")

    elif (client_commands.get(name_command) == "upload"):
        if (is_file_exist(file_name)):
            send_status(client, name_command, 200)
            upload(file_name)
        else:
            no_file = "File: " + file_name + " is not exist."
            send_status_and_message(client, name_command, 500, no_file)
    else:
        send_status_and_message(client, name_command, 500, "Unknown command")

def send_status_and_message(client, request, status, message):
    message = str("" + request + " " + str(status) + " " + message)
    client.send(message.encode('utf-8'))

def send_status(client, request, status):
    message = str("" + request + " " + str(status))
    client.send(message.encode('utf-8'))

def is_file_exist(file_name):
    return os.path.exists(file_name)

def delete(file_name):
    pass

def upload(file_name):
    f = open(file_name, 'wb')
    data = client.recv(BUFFER_SIZE)
    while (data):
        f.write(data)
        data = client.recv(BUFFER_SIZE)
    f.close()


def download(file_name):
    f = open (file_name, "rb")
    data_file = f.read(BUFFER_SIZE)
    while (data_file):
        client.send(data_file)
        data_file = f.read(BUFFER_SIZE)

    f.close()

def server_cli():
    while True:
        command = input_command()
        parsed_data = parse_server_command(command)
        if (parsed_data == False):
            pass
        elif (len(parsed_data) == 2):
            command, body = parsed_data
            handle_server_command(command, body)

def parse_server_command(command):
    command = command.split()
    if (len(command) == 0):
        return False

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
        os._exit(1)



def input_command():
    return input()

def show_server_menu():
    for x in help_list:
        print(x, ": ", help_list[x])


show_start_message();
server_cli = threading.Thread(target=server_cli)
server_cli.start()



while True:
    client, addr = server.accept()
    print("[*] Accepted connection from: %s:%d" % (addr[0], addr[1]))

    client_handle = threading.Thread(target=handle_client, args=(client,))
    client_handle.start()
