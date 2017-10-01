import select
import socket
import sys
import time
import queue as Queue
# from multiprocessing import Queue

# Create a TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.setblocking(0)

# Bind the socket to the port
server_address = ('localhost', 10000)
print (sys.stderr, 'starting up on %s port %s' % server_address)
server.bind(server_address)

# Listen for incoming connections
server.listen(5)

# Sockets from which we expect to read
inputs = [ server ]

# Sockets to which we expect to write
outputs = [ ]

# Outgoing message queues (socket:Queue)
message_queues = {}

while inputs:
    timeout = 1

    # Wait for at least one of the sockets to be ready for processing
    readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)

    for s in readable:
        print(readable)
        if s is server:
            # A "readable" server socket is ready to accept a connection
            connection, client_address = s.accept()
            # print (sys.stderr, 'new connection from', client_address)
            connection.setblocking(0)
            inputs.append(connection)

            # Give the connection a queue for data we want to send
            message_queues[connection] = Queue.Queue()
        else:
            data = s.recv(1024)
            if data:
                # A readable client socket has data
                # print (sys.stderr, 'received "%s" from %s' % (data, s.getpeername()))
                message_queues[s].put(data)
                # Add output channel for response
                if s not in outputs:
                    outputs.append(s)
                else:
                # Interpret empty result as closed connection
                    print (sys.stderr, 'closing', client_address, 'after reading no data')
                    # Stop listening for input on the connection
                    if s in outputs:
                        outputs.remove(s)
                    inputs.remove(s)
                    s.close()

                    # Remove message queue
                    del message_queues[s]
