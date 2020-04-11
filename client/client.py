from socket import *
import json
import random


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
        s.connect(server)
        return s
    except OSError:
        print("error connecting to server")
        return None


def key_exchange(servers, dst):
    server_socks = []

    for i in range(len(servers)):
        server = servers[i]
        key = key_generator()
        s = create_connection(server)
        if not s:
            return

        try:
            s.send(f"1\n{key}\n{servers[i+1][0]},{server[i+1][1]}".encode())
        except IndexError:
            s.send(f"1\n{key}\n{dst[0]},{dst[1]}".encode())
        except OSError:
            print("connection error")
            s.close()
            return

        try:
            s.settimeout(3)
            answer = s.recv(1024)
        except timeout:
            print("id not available")
            return
        print(answer)
        server_socks.append(s)
    return server_socks


def main():
    dst = ("172.217.22.36", 80)
    print(get_server_list())
    print(select_random_servers(get_server_list()))
    '''
    server = select_first_server(get_server_list())
    server_socket = key_exchange(server)
    server_socket.close()
    '''

if __name__ == '__main__':
    main()
