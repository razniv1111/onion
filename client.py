from socket import *
import json
import random

def get_server_list():
    with open("server_list.json", "r") as f:
        data = json.load(f)
    return data

def select_first_server(server_list):
    return random.choice(list(server_list.keys()))

def key_generator():
    # will be changed to a proper encryption
    return random.randrange(0,100000)

def id_generator():
    return random.randrange(0,1000)

def create_connection(server):
    s = socket(AF_INET, SOCK_STREAM)
    try:
        s.connect(server)
        return s
    except OSError:
        print("error connecting to server")
        return None

def key_exchange(server):
    id = id_generator()
    key = key_generator()
    s = create_connection(server)
    if not s:
        return

    try:
        s.send("1\n" + id + "\n" + key)
    except OSError:
        print("connection error")
        s.close()
        return

    try:
        s.settimeout(3)
        s.recv(1024)
    except timeout:
        print("id not available")
        return
    return s

def main():
    servers = get_server_list()
    print(select_first_server(servers))

if __name__ == '__main__':
    main()
