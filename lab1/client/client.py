import socket
from commands import client_commands

# host = '192.168.0.110'
host = ''
port = 9001

#host = '127.0.0.1'
#port = 8081

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

def handle_input_request(request):
    client.send((request).encode('utf-8'))
    command = request.split()
    name_command = command[0]
    if (len(command) == 2):
        body = command[1]
    else:
        body = ""
    print name_command, body
    if (client_commands.get(name_command) == "download"):
        download(body)
    if (client_commands.get(name_command) == "upload"):
        upload(body)
    if (client_commands.get(name_command) == "delete"):
        delete(body)
    if (client_commands.get(name_command) == "exit"):
        exit()

def download(file_name):
    f = open(file_name, 'wb')
    data = client.recv(1024)
    while (data):
        f.write(data)
        data = client.recv(1024)
    f.close()
    print(file_name + " was downloaded")

def upload(file_name):
    f = open (file_name, "rb")
    data_file = f.read(1024)
    while (data_file):
        client.send(data_file)
        data_file = f.read(1024)

    f.close()
    print(file_name + " was uploaded")


def delete(file_name):
    pass

def exit():
    pass

def check_valid_request(request):
    return True

def input_request():
    return raw_input("");

def show_status():
    pass

def show_error_message(error):
    print(error)

while True:
    request = input_request()
    if (check_valid_request(request)):
        handle_input_request(request)
    else:
        show_error_message("Not Valid Command")
