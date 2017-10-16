from commands import server_commands, help_list
from datetime import datetime
import os
import os.path

def server_cli(server):
    show_start_message()
    while True:
        command = input()
        parsed_data = parse_server_command(command)
        if (parsed_data == False):
            pass
        elif (len(parsed_data) == 2):
            command, body = parsed_data
            handle_server_command(command, body, server)

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


def handle_server_command(command, body, server):
    if (server_commands.get(command) == "help"):
        show_server_menu()
    if (server_commands.get(command) == "echo"):
        print(body)
    if (server_commands.get(command) == "time"):
        print("Server time: " + str(datetime.now())[:19])
    if (server_commands.get(command) == "exit"):
        server.close()
        os._exit(1)

def show_server_menu():
    for x in help_list:
        print(x, ": ", help_list[x])


def show_start_message():
    show_server_menu()
