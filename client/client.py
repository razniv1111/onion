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


def key_exchange_with_first_server(servers):

    key = key_generator()
    s = create_connection(servers[0])
    if not s:
        return

    try:
        s.send(f"1\n{key}\n{servers[1][0]},{servers[1][1]}".encode())
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
    return s


def setup_all_servers(s, servers, dst):
    for i in range(1,len(servers)):
        key = key_generator()
        header = '2\n'*i
        try:
            s.send(f"{header}1\n{key}\n{servers[i+1][0]},{servers[i+1][1]}").encode()
        except IndexError:
            s.send(f"{header}1\n{key}\n{dst[0]},{dst[1]}").encode()
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

def main():

    server = select_random_servers(get_server_list())
    server_socket = key_exchange_with_first_server(server)
    setup_all_servers(server_socket,server,["www.google.com",80])
    server_socket.close()

if __name__ == '__main__':
    main()
