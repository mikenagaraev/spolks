import socket
import threading
from commands import client_commands
import os
import os.path
import sys
import errno
import time

# host = '192.168.100.5'
host = ''
port = 9001

BUFFER_SIZE = 2048
TIMEOUT = 30

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
        download(body, request)

    if (client_commands.get(name_command) == "upload"):
        upload(body, request)

    if (client_commands.get(name_command) == "delete"):
        delete(body, request)

    if (client_commands.get(name_command) == "exit"):
        os._exit(1)

def wait_for_ack(command_to_compare):
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

def handle_disconnect(request, command):
    global client

    print("Remote Disconnect")
    client.close()

    while(1):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((host, port))
            client.send(request.encode('utf-8'))
            wait_for_ack(command)
            break;
        except socket.error as er:
            print("no connetion")

        time.sleep(1)

def send_ok():
    client.send("OK".encode('utf-8'))

def get_data():
    return client.recv(BUFFER_SIZE).decode('utf-8')

def send_data(data):
    client.send(str(data).encode('utf-8'))

def is_file_exist(file_name):
    return os.path.exists(file_name)

def download(file_name, request):
    size = int(get_data()) #1

    send_ok() #2

    send_data(0) #3

    data_size_recv = int(get_data()) #4

    if (data_size_recv == 0):
        f = open(file_name, "wb")
    else:
        f = open(file_name, "rb+")

    send_ok() #5

    while (data_size_recv < size):
        try:
            data = client.recv(BUFFER_SIZE)
            f.seek(data_size_recv, 0)
            f.write(data)
            data_size_recv += len(data)
            send_data(data_size_recv)

            progress = (data_size_recv / (size)) * 100
            sys.stdout.write("Download progress: %d%% \r" %progress)
            sys.stdout.flush()

        except socket.error as e:
            handle_disconnect(request, "download")
            size = int(get_data())
            send_ok()
            send_data(data_size_recv)
            data_size_recv = int(get_data())
            send_ok()

        except KeyboardInterrupt:
            print("KeyboardInterrupt was handled")
            f.close()
            client.close()
            os._exit(1)

    f.close()
    print(file_name + " was downloaded")

def upload(file_name):
    f = open(file_name, "rb")
    data_file = f.read(BUFFER_SIZE)
    size = int(os.path.getsize(file_name))
    client.send(str(size).encode('utf-8'))
    data_size_recv = 0

    while (client.recv(2).decode('utf-8') != "OK"):
        pass

    while (data_size_recv != size):
        client.sendall(data_file)
        data_file = f.read(BUFFER_SIZE)
        data_size_recv = int(client.recv(BUFFER_SIZE).decode('utf-8'))

        progress = (data_size_recv / size) * 100
        sys.stdout.write("Upload progress: %d%% \r" %progress)
        sys.stdout.flush()

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

def show_status():
    pass

def show_error_message(error):
    print(error)


while True:
    try:
        request = input()
        if (check_valid_request(request)):
            handle_input_request(request)
    except KeyboardInterrupt:
        print("KeyboardInterrupt was handled")
        client.close()
        os._exit(1)

    # else:
    #     show_error_message("Not Valid Command")
