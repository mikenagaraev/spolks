import socket
from commands import client_commands
import os
import os.path

host = '192.168.100.5'
port = 9001

BUFFER_SIZE = 1024

#host = '127.0.0.1'
#port = 8081

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

def handle_input_request(request):
    client.sendall((request).encode('utf-8'))
    command = request.split()
    name_command = command[0]

    if (len(command) == 2):
        body = command[1]

    if (wait_for_ack(name_command) == False):
        return

    if (client_commands.get(name_command) == "download"):
        download(body)

    if (client_commands.get(name_command) == "upload"):
        upload(body)

    if (client_commands.get(name_command) == "delete"):
        delete(body)

    if (client_commands.get(name_command) == "exit"):
        os._exit(1)

def wait_for_ack(command_to_compare):
    # TIMEOUT = 30
    while True:
        response = client.recv(BUFFER_SIZE).decode('utf-8').split(" ", 2)

        if not response:
            return False

        sent_request = response[0]
        status = response[1]

        if (len(response) > 2):
            message = response[2]
        else: message = None

        if (command_to_compare == sent_request and int(status) == 200):
            return True
        elif (message):
            print(message)
            return False
        else:
            return False


def download(file_name):
    f = open(file_name, 'wb')
    size = int(client.recv(BUFFER_SIZE).decode('utf-8'))
    client.send("OK".encode('utf-8'))
    data_size_recv = 0

    while (data_size_recv != size):
        data = client.recv(BUFFER_SIZE)
        f.write(data)
        data_size_recv += len(data)

    f.close()
    print(file_name + " was downloaded")

def upload(file_name):
    f = open(file_name, "rb")
    data_file = f.read(BUFFER_SIZE)
    size = os.path.getsize(file_name)
    client.send(str(size).encode('utf-8'))

    while (client.recv(2).decode('utf-8') != "OK"):
        pass

    while (data_file):
        client.sendall(data_file)
        data_file = f.read(BUFFER_SIZE)

    f.close()
    print(file_name + " was uploaded")


def delete(file_name):
    pass

def exit():
    pass

def check_valid_request(request):
    command = request.split()
    if (len(command) == 0):
        return False
    else: return True

def input_request():
    return input();

def show_status():
    pass

def show_error_message(error):
    print(error)

while True:
    request = input_request()
    if (check_valid_request(request)):
        handle_input_request(request)
    # else:
    #     show_error_message("Not Valid Command")
