import socket
from commands import client_commands
import os
import os.path
import sys
import errno
import time
import re

HOST = ''
PORT = 9001

BUFFER_SIZE = 1024
TIMEOUT = 20

OK_STATUS = 200


def wait_ok():
    while (client.recv(2).decode('utf-8') != "OK"):
        print("wait for OK")

def send_ok():
    client.send("OK".encode('utf-8'))

def get_data():
    return client.recv(BUFFER_SIZE).decode('utf-8')

def send_data(data):
    client.send(str(data).encode('utf-8'))


def handle_input_request(request):
    command = request.split()
    name_command = command[0]

    if (len(command) == 2):
        body = command[1]

    if (client_commands.get(name_command) == "echo"):
        send_data(request)
        if (wait_for_ack(name_command) == False):
            return
        echo(body)

    if (client_commands.get(name_command) == "time"):
        send_data(request)
        if (wait_for_ack(name_command) == False):
            return
        get_time()

    if (client_commands.get(name_command) == "download"):
        send_data(request)
        if (wait_for_ack(name_command) == False):
            return
        download(body, request)

    if (client_commands.get(name_command) == "upload"):
        if (is_file_exist(body)):
            send_data(request)
            if (wait_for_ack(name_command) == False):
                return
            upload(body, request)
        else:
            show_error_message("No such file exists")

    if (client_commands.get(name_command) == "delete"):
        send_data(request)
        if (wait_for_ack(name_command) == False):
            return
        delete(body, request)

    if (client_commands.get(name_command) == "exit"):
        send_data(request)
        if (wait_for_ack(name_command) == False):
            return
        client.close()
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

        if (command_to_compare == sent_request and int(status) == OK_STATUS):
            return True
        elif (message):
            print(message)
            return False
        else:
            return False

def is_server_available(request, command):
    global client

    client.close()

    i = TIMEOUT

    while(i > 0):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((HOST, PORT))
            client.send(request.encode('utf-8'))
            wait_for_ack(command)
            return True

        except socket.error as er:
            sys.stdout.write("Waiting for a server: %d seconds \r" %i)
            sys.stdout.flush()

        i -= 1
        time.sleep(1)

    sys.stdout.flush()
    print("\nServer was disconnected")
    sys.stdout.flush()
    return False


def is_file_exist(file_name):
    return os.path.exists(file_name)

def echo(body):
    send_data(body)
    print(get_data())

def get_time():
    print(get_data())

def download(file_name, request):
    size = int(get_data()) #1

    send_data(0) #3

    data_size_recv = int(get_data()) #4

    if (data_size_recv == 0):
        f = open(file_name, "wb")
    else:
        f = open(file_name, "rb+")

    while (data_size_recv < size):
        try:
            data = client.recv(BUFFER_SIZE)
            f.seek(data_size_recv, 0)
            f.write(data)
            data_size_recv += len(data)

            progress = (data_size_recv / (size)) * 100
            sys.stdout.write("Download progress: %d%% \r" %progress)
            sys.stdout.flush()

        except socket.error as e:
            if(is_server_available(request, "download")):
                size = int(get_data())
                send_data(data_size_recv)
                data_size_recv = int(get_data())
                print("\n")
            else:
                f.close()
                client.close()
                os._exit(1)

        except KeyboardInterrupt:
            print("KeyboardInterrupt was handled")
            f.close()
            client.close()
            os._exit(1)

    f.close()
    print("\n" + file_name + " was downloaded")

def upload(file_name, request):
    f = open (file_name, "rb+")

    size = int(os.path.getsize(file_name))

    send_data(size) #1

    wait_ok() #2

    send_data(0) #3

    data_size_recv = int(get_data()) #4

    wait_ok() #5

    f.seek(data_size_recv, 0)

    while (data_size_recv < size):
        try:
            data_file = f.read(BUFFER_SIZE)
            client.send(data_file)
            received_data = get_data()

            progress = (data_size_recv / size) * 100
            sys.stdout.write("Upload progress: %d%% \r" %progress)
            sys.stdout.flush()

        except socket.error as e:
            if(is_server_available(request, "upload")):
                send_data(size)
                wait_ok()
                send_data(data_size_recv)
                data_size_recv = int(get_data())
                wait_ok()
                print("\n")
            else:
                f.close()
                client.close()
                os._exit(1)

        except KeyboardInterrupt:
            print("KeyboardInterrupt was handled")
            f.close()
            client.close()
            os._exit(1)

        if (received_data):
            data_size_recv = int(received_data)
            f.seek(data_size_recv, 0)

    f.close()
    print("\n" + file_name + " was uploaded")


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

def show_start_message():
    print("\nWelcome to client cli!")

is_valid_address = False

REGULAR_IP = '^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$'
regex = re.compile(REGULAR_IP)

#
# while (is_valid_address == False):
#     addr = input("\nInput host addres: ")
#     if (regex.match(addr)):
#         is_valid_address = True
#         HOST = addr
#     else:
#         try:
#             HOST = socket.gethostbyname(addr)
#             is_valid_address = True
#         except socket.error:
#             print("Please, input valid address")
#             is_valid_address = False

show_start_message()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))


while True:

    try:
        request = input()
        if (check_valid_request(request)):
            handle_input_request(request)
    except KeyboardInterrupt:
        print("KeyboardInterrupt was handled")
        client.close()
        os._exit(1)
