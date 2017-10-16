import socket
import select
import threading
from datetime import datetime
import sys
import os
import os.path
import time
from commands import server_commands, client_commands, help_list

IP = ''

PORT = 9001
BUFFER_SIZE = 1024

TIMEOUT = 20

OK_STATUS = 200
SERVER_ERROR = 500




def send_status_and_message(client, request, status, message):
    message = str("" + request + " " + str(status) + " " + message)
    client.send(message.encode('utf-8'))

def send_status(client, request, status):
    message = str("" + request + " " + str(status))
    client.send(message.encode('utf-8'))

def is_file_exist(file_name):
    return os.path.exists(file_name)

def handle_client(client):
    while True:
        if (client["is_closed"] == False):
            request = client['socket'].recv(BUFFER_SIZE).decode('utf-8')
            request = request.strip()
            if request != '':
                print("[*] Received: %s" %request)
                handle_client_request(client, request)

def echo(client, body):
    time.sleep(0.01)
    send_data(client, body)

def send_time(client):
    server_time = "Server time: " + str(datetime.now())[:19]
    send_data(client, server_time)

def exit_client(client):
    clients_pool.remove(client)
    client['is_closed'] = True
    client['socket'].close()

def handle_client_request(client, request):
    command = request.split()
    name_command = command[0]

    if (len(command) == 2):
        body = command[1]

    if (client_commands.get(name_command) == "download"):
        if (is_file_exist(body)):
            send_status(client['socket'], name_command, OK_STATUS)
            download(client, body)
        else:
            no_file = "File: " + body + " is not exist."
            send_status_and_message(client['socket'], name_command, SERVER_ERROR, "No such file")


    elif (client_commands.get(name_command) == "upload"):
        send_status(client['socket'], name_command, OK_STATUS)
        upload(client, body)

    elif (client_commands.get(name_command) == "echo"):
        send_status(client['socket'], name_command, OK_STATUS)
        echo(client, body)

    elif (client_commands.get(name_command) == "time"):
        send_status(client['socket'], name_command, OK_STATUS)
        send_time(client)

    elif (client_commands.get(name_command) == "exit"):
        send_status(client['socket'], name_command, OK_STATUS)
        exit_client(client)

    elif (client_commands.get(name_command) == "delete"):
        if (is_file_exist(body)):
            send_status(client['socket'], name_command, OK_STATUS)
            delete(client, body)
        else:
            no_file = "File: " + body + " is not exist."
            send_status_and_message(client['socket'], name_command, SERVER_ERROR, "No such file")

    else:
        send_status_and_message(client['socket'], name_command, SERVER_ERROR, "Unknown command")

def delete(client, file_name):
    pass

def check_client_available(client_ip, command):
    i = TIMEOUT
    while(i > 0):
        waiting_client = search_by_ip(clients_pool, client_ip)
        sys.stdout.write("Waiting for a client: %d seconds \r" %i)
        sys.stdout.flush()

        if(waiting_client):
            sys.stdout.flush()
            print("\nClient has returned")
            sys.stdout.flush()
            return

        i -= 1
        time.sleep(1)


    waiting_client = search_by_ip(waiting_clients, client_ip)
    if (len(waiting_clients) > 0 and waiting_client != False):
        waiting_clients.remove(waiting_client)

    if (command == "upload"):
	    os.remove(waiting_client['file_name'])

    sys.stdout.flush()
    print("\nClient was disconnected")
    sys.stdout.flush()


def search_by_ip(list, ip):
    found_client = [element for element in list if element['ip'] == ip]
    return found_client[0] if len(found_client) > 0 else False

def search_by_socket(list, socket):
    found_client = [element for element in list if element['socket'] == socket]
    return found_client[0] if len(found_client) > 0 else False



def save_to_waiting_clients(ip, command, file_name, progress):
    waiting_clients.append(
        {
            'ip': ip,
            'command': command,
            'file_name': file_name,
            'progress': progress
        })

def handle_disconnect(client, command, file_name, progress):
    save_to_waiting_clients(client['ip'], command, file_name, progress)
    clients_pool.remove(client)
    client['socket'].close()
    check_client_available(client['ip'], command)

def wait_ok(client):
    while (client['socket'].recv(2).decode('utf-8') != "OK"):
        print("wait for OK")

def send_ok(client):
    client['socket'].send("OK".encode('utf-8'))

def get_data(client):
    return client['socket'].recv(BUFFER_SIZE).decode('utf-8')

def send_data(client, data):
    client['socket'].send(str(data).encode('utf-8'))

def download(client, file_name):
    f = open (file_name, "rb+")

    size = int(os.path.getsize(file_name))

    send_data(client, size) #1

    wait_ok(client) #2

    waiting_client = search_by_ip(waiting_clients, client['ip'])
    if (len(waiting_clients) > 0 and waiting_client != False):
        waiting_clients.remove(waiting_client)

    data_size_recv = int(get_data(client)) #3

    if (waiting_client):
        if (waiting_client['file_name'] == file_name and waiting_client['command'] == 'download'):
            data_size_recv = int(waiting_client['progress'])
            send_data(client, data_size_recv)
    else:
        send_data(client, data_size_recv) #4

    wait_ok(client) #5

    f.seek(data_size_recv, 0)

    while (data_size_recv < size):
        try:
            data_file = f.read(BUFFER_SIZE)
            client['socket'].sendall(data_file)
            received_data = get_data(client)

        except socket.error as e:
            f.close()
            handle_disconnect(client, "download", file_name, data_size_recv)
            client['is_closed'] = True
            return

        except KeyboardInterrupt:
            server.close()
            client.socket.close()
            os._exit(1)

        if received_data:
            data_size_recv = int(received_data)
            f.seek(data_size_recv)

        time.sleep(0.05)

    f.close()

def upload(client, file_name):
    size = int(get_data(client)) #1

    send_ok(client) #2

    data_size_recv = get_data(client) #3
    if (data_size_recv):
        data_size_recv = int(data_size_recv)

    waiting_client = search_by_ip(waiting_clients, client['ip'])
    if (len(waiting_clients) > 0 and waiting_client != False):
        waiting_clients.remove(waiting_client)

    if (waiting_client):
        if (waiting_client['file_name'] == file_name and waiting_client['command'] == 'upload'):
            data_size_recv = int(waiting_client['progress'])
            send_data(client, data_size_recv)
    else:
        send_data(client, data_size_recv) #4

    send_ok(client) #5

    if (data_size_recv == 0):
        f = open(file_name, "wb")
    else:
        f = open(file_name, "rb+")


    f.seek(data_size_recv, 0)

    while (data_size_recv < size):
        try:
            data = client['socket'].recv(2, socket.MSG_OOB)

        except socket.error as e:
            data = False

        try:
            if data:
                print ("Urgent data")
                print (data.decode('utf-8'))
            else:
                data = client['socket'].recv(BUFFER_SIZE)
                f.write(data)
                data_size_recv += len(data)
                send_data(client, data_size_recv)
                f.seek(data_size_recv, 0)

        except socket.error as e:
            f.close()
            handle_disconnect(client, "upload", file_name, data_size_recv)
            client['is_closed'] = True
            return

        time.sleep(0.05)


    f.close()

def server_cli():
    while True:
        command = input()
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


def show_clients():
    list_len = len(clients_pool)
    if (list_len == 0):
        print("\nNo clients available")
    for i in range(0, list_len):
        print("\n" + "Client " + str(i+1) + " info: ")
        print("ip: ", clients_pool[i]['ip'])
        print("port: ", clients_pool[i]['port'])
        print("closed: ", clients_pool[i]['is_closed'])

def handle_server_command(command, body):
    if (server_commands.get(command) == "help"):
        show_server_menu()
    if (server_commands.get(command) == "echo"):
        print(body)
    if (server_commands.get(command) == "show_clients"):
        show_clients()
    if (server_commands.get(command) == "time"):
        print("Server time: " + str(datetime.now())[:19])
    if (server_commands.get(command) == "exit"):
        server.close()
        os._exit(1)

def show_server_menu():
    for x in help_list:
        print(x, ": ", help_list[x])


def show_start_message():
    print("Hello, listened on %s:%d" %(IP, PORT))
    show_server_menu()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((IP, PORT))
server.listen(2)

show_start_message();
server_cli = threading.Thread(target=server_cli)
server_cli.start()

clients_pool = []
waiting_clients = []


client_ID = 0

while True:
        client, client_info = server.accept()

        client_ip = client_info[0]
        client_port = client_info[1]

        print("[*] Accepted connection from: %s:%d" % (client_ip, client_port))

        client_obj = {
                        "id": client_ID,
                        "socket": client,
                        "ip": client_ip,
                        "is_closed": False,
                        "port": client_port
                    }

        clients_pool.append(client_obj)

        client_handle = threading.Thread(target=handle_client, args=(clients_pool[len(clients_pool) - 1], ))
        client_handle.start()
        client_ID += 1
