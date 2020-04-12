from socket import *
import json
import random
import time


def get_server_list():
    with open("server_list.json", "r") as f:
        data = json.load(f)
    return data


def select_random_servers(server_list):
    server_ids = list(range(0, len(server_list)))
    random.shuffle(server_ids)
    server_ids = server_ids[0:3]
    return list(map(lambda x: server_list[str(x)], server_ids))


def key_generator():
    # will be changed to a proper encryption
    return random.randrange(0, 100000)


def create_connection(server):
    s = socket(AF_INET, SOCK_STREAM)
    try:
        s.connect(tuple(server))
        return s
    except OSError:
        print("error connecting to server")
        return None


def key_exchange_with_first_server(servers):
    key = key_generator()
    s = create_connection(servers[0])
    if not s:
        return

    try:
        s.send(f"1\n{key}\n{servers[1][0]},{servers[1][1]}".encode())
    except OSError:
        print(f"connection error with {s.getpeername()}")
        s.close()
        return

    try:
        s.settimeout(3)
        answer = s.recv(1024).decode()
    except timeout:
        print("id not available")
        return
    print('received from first server on connection:', answer, end='\n\n')
    return s


def setup_all_servers(s, servers, dst):
    for i in range(1, len(servers)):
        key = key_generator()
        header = '2\n' * i
        try:
            s.send(f"{header}1\n{key}\n{servers[i + 1][0]},{servers[i + 1][1]}".encode())
        except IndexError:
            s.send(f"{header}1\n{key}\n{dst[0]},{dst[1]}".encode())
        except OSError:
            print("connection error")
            s.close()
            return

        try:
            s.settimeout(3)
            answer = s.recv(1024).decode()
        except timeout:
            print("id not available")
            return
        print('received from first server:', answer, end='\n\n')


def main():
    server = select_random_servers(get_server_list())
    #server = [["172.18.180.241", 1230], ["172.18.180.241", 1231], ["172.18.180.241", 1232]]
    print(f'servers list: {server}')
    server_socket = key_exchange_with_first_server(server)
    setup_all_servers(server_socket, server, ['192.168.42.167', 14067])
    server_socket.send('2\n2\n2\nHIIII'.encode())
    print(server_socket.recv(1024).decode())
    server_socket.close()


if __name__ == '__main__':
    main()
