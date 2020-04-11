"""
Onion server
"""
import socket
from select import select
import collections
import time

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
            return sock


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

    lines = data.splitlines()

    if lines[0] != '1':
        print(f'error!, connected client {connection.getpeername()} tries to change key')
        return

    connection_id, connection_key, destination = lines[1], lines[2], lines[3]

    if find_in_connections('id', connection):
        print('connection denied')
        connection.close()
        no_key_set.remove(connection)
        return
    dst_ip, dst_port = destination.split(',')
    dst_port = int(dst_port)
    connection.send('OK'.encode())

    dst_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dst_socket.connect((dst_ip, dst_port))

    connections.append(Connection(src=connection, key=connection_key, dst=dst_socket))

    no_key_set.remove(connection)
    rlist.append(connection, dst_socket)
    wlist.append(dst_socket)
    xlist.append(dst_socket)


def send_forward(data, dst):
    """removes encryption and sends forward"""""
    dst.send(data)


def send_backward(data, src):
    src.send()


def forward_data(connection):
    data = connection.recv(BUFF_SIZE).decode()
    if not data:
        connection_closed(connection)
        return

    connection_data = find_connection(connection)
    if not connection_data:
        print(f'error, {connection.getpeername()} not found')
        return

    if connection_data.src == socket:
        if data[:2] != '2\n':
            print(f'error, {connection.getpeername()} tries to establish key')
            return

        send_forward(data[3:], connection_data.dst)
    else:
        send_backward(data, connection_data.src)
    print(connection.getpeername(), 'data=', data)


def deal_with_massage(connection):
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
    print(f'new client from {client_address}')
    no_key_set.append(client_socket)
    wlist.append(client_socket)
    xlist.append(client_socket)


def main_loop(server_socket):
    global no_key_set, rlist, wlist, xlist

    rlist.append(server_socket)

    while True:
        print()
        print((len(rlist), len(no_key_set)), len(wlist), len(xlist))
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
