"""
Onion server
"""
import socket
from select import select
import collections
import time

Link = collections.namedtuple('Link', ['src', 'dst'])
Connection = collections.namedtuple('Connection', ['socket', 'id', 'key'])

connections = []

rlist, wlist, xlist = [], [], []
no_key_set = []
BUFF_SIZE = 2048

connections = []


def create_server_socket(port):
    ip = socket.gethostbyname(socket.gethostname())
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen(2)
    print(f'waiting for connection at {(ip, port)}')
    return server_socket


def find_in_connections(field, value):
    """
    searches for value in connections
    :param field: field name
    :param value: value
    :return: list of matching connections
    """
    index = Connection._fields.index(field)
    return [connection for connection in connections if connection[index] == value]


def deal_with_massage(connection):
    # needs to establish key
    if connection in no_key_set:
        print('connect')
        data = connection.recv(BUFF_SIZE).decode()
        print(data)
        lines = data.splitlines()
        if lines[0] != '1':
            print(f'error!, connected client {connection.getpeername()} tries to change key')
            return
        connection_id = lines[1]
        connection_key = lines[3]
        if find_in_connections('id', connection):
            connection.close()
            no_key_set.remove(connection)
            return
        connection.send('OK')
        connections.append(Connection(socket == connection, id=connection_id, key=connection_key))
        no_key_set.remove(connection)
        rlist.append(connection)
    else:
        print('data=', connection.recv(BUFF_SIZE).decode())


def accept_connection(server_socket):
    global no_key_set, wlist, xlist
    client_socket, client_address = server_socket.accept()
    print(f'new client from {client_address}')
    no_key_set.append(client_socket)
    wlist.append(client_socket)
    xlist.append(client_socket)


def main_loop(server_socket):
    rlist.append(server_socket)

    while True:
        print()
        print(len(rlist + no_key_set), len(wlist), len(xlist))
        received, ready_to_write, excepted = select(rlist + no_key_set, wlist, xlist)
        print('new: ', len(received), len(ready_to_write), len(excepted))

        for connection in received:
            if server_socket == connection:
                accept_connection(connection)
                continue

            deal_with_massage(connection)
        time.sleep(1)


def main():
    server_socket = create_server_socket(port=1234)
    main_loop(server_socket)
    server_socket.close()


if __name__ == '__main__':
    main()
