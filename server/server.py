"""
Onion server
"""
import socket
from select import select
import collections
import time
import sys

Connection = collections.namedtuple('Connection', ['src', 'key', 'dst'])

connections = []

rlist, wlist, xlist = [], [], []
no_key_set = []
BUFF_SIZE = 2048

connections = []
links = []


def create_server_socket(port):
    """ creates server socket at the computer IP at the specified ip"""
    ip = socket.gethostbyname(socket.gethostname())

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen(2)

    print(f'waiting for connection at {(ip, port)}')

    return server_socket


def find_in_connections(field, value):
    """
    searches for values in connections
    :param field: field name
    :param value: value
    :return: list of matching connections
    """
    index = Connection._fields.index(field)
    return [connection for connection in connections if connection[index] == value]


def find_connection(sock):
    """
    finds relevent connection for socket
    """
    for connection in connections:
        if sock in connection:
            return connection


def connection_closed(connection):
    """ closes connection and removes from all lists """

    def remove_from_list(list, connection):
        """ removes connection from list if exists"""
        if connection in list:
            list.remove(connection)

    global no_key_set, rlist, wlist, xlist
    print(f'connection {connection.getpeername()} closed')

    connection.close()

    if connection in no_key_set:
        no_key_set.remove(connection)
    if connection in rlist:
        rlist.remove(connection)
    if connection in wlist:
        wlist.remove(connection)
    if connection in xlist:
        xlist.remove(connection)


def establish_key(connection):
    """
    accepts key from new connection. if valid connection is moved from no_key_set to rlist
    :param connection:
    :return:
    """
    global no_key_set, rlist, wlist, xlist

    data = connection.recv(BUFF_SIZE).decode()
    if not data:
        connection_closed(connection)
        return

    print(f'establishing key with {connection.getpeername()}', end='\n\n')
    lines = data.splitlines()

    if lines[0] != '1':
        print(f'error!, connection client {connection.getpeername()} doesnt use 1 flag')
        return

    connection_key, destination = lines[1], lines[2]

    dst_ip, dst_port = destination.split(',')
    dst_port = int(dst_port)
    connection.send('OK'.encode())

    dst_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dst_socket.connect((dst_ip, dst_port))

    connections.append(Connection(src=connection, key=connection_key, dst=dst_socket))

    no_key_set.remove(connection)
    rlist.extend([connection, dst_socket])
    wlist.append(dst_socket)
    xlist.append(dst_socket)


def send_forward(data, dst):
    """removes encryption and sends forward"""""
    print(data, end='\n\n')
    dst.send(data.encode())


def send_backward(data, src):
    print(data, end='\n\n')
    src.send(data.encode())


def forward_data(connection):
    data = connection.recv(BUFF_SIZE).decode()

    if not data:
        connection_closed(connection)
        return
    print(f'forwarding from {connection.getpeername()}', end='')

    connection_data = find_connection(connection)
    if not connection_data:
        print(f'error, {connection.getpeername()} not found')
        return

    if connection_data.src == connection:
        if data[:2] != '2\n':
            print(f'error, {connection.getpeername()} tries to establish key')
            return
        print(f' sent to {connection_data.dst.getpeername()}')
        send_forward(data[2:], connection_data.dst)
    else:
        print(connection_data.src)
        print('sent to', connection_data.src.getpeername())
        send_backward(data, connection_data.src)


def deal_with_message(connection):
    """
    receves massage and does the needed action
    :param connection: the socket to deal with
    """

    if connection in no_key_set:
        establish_key(connection)
    else:
        forward_data(connection)


def accept_connection(server_socket):
    """
    accepts a new connection and appends it to no_key_set, wlist, xlist
    """
    global no_key_set, wlist, xlist
    client_socket, client_address = server_socket.accept()
    print(f'new client from {client_address}', end='\n\n')
    no_key_set.append(client_socket)
    wlist.append(client_socket)
    xlist.append(client_socket)


def main_loop(server_socket):
    global no_key_set, rlist, wlist, xlist

    rlist.append(server_socket)

    while True:
        received, ready_to_write, excepted = select(rlist + no_key_set, wlist, xlist)

        for connection in received:
            if server_socket == connection:
                accept_connection(connection)
                continue

            deal_with_message(connection)
        # time.sleep(5)


def main():
    if len(sys.argv) < 2:
        port = 1230
    else:
        port = int(sys.argv[1])
    server_socket = create_server_socket(port=port)
    main_loop(server_socket)
    server_socket.close()


if __name__ == '__main__':
    main()
