#!/usr/bin/env python3

# rootless ssh "server". Allows you to establish an SSH session
# and run a shell or command as the user who runs the script
# 
#
# "initial tests" - polprog 10/2021
# "oh no, it works" - jercos, 10/2021
# "code cleanup, add command line opts" - polprog, 10/2021
# TODO: add client pubkey auth
# TODO: fix bug when pressing ^C instead of entering password in client crashes server
#       (ValueError on select(), socket fd becomes -1)
# TODO: fix curses maybe? 

import select
import socket
import subprocess
import paramiko
import os
import sys
import pty
import fcntl
import argparse

host_key = None
client_username = None
client_password = None
#user_key = None
address = None
port = None
shellpath = None

authenticated = lambda a, b: False

class Client(paramiko.ServerInterface):
    def __init__(self, s_client, transport):
        self.s_client = s_client
        transport.add_server_key(host_key)
        transport.start_server(server=self)
        self.transport = transport
        self.channel = None
        self.shell_request = False
        self.exec_request = False
        self.username = None
        self.session = False
        self.subprocess = False
        self.ptym, self.ptys = pty.openpty()
        flag = fcntl.fcntl(self.ptym, fcntl.F_GETFL)
        fcntl.fcntl(self.ptym, fcntl.F_SETFL, flag | os.O_NONBLOCK)
 
    def fileno(self):
        if self.channel:
            return self.channel.fileno()
        return self.s_client.fileno()

    def check_channel_request(self, kind, chanid):
        print(f"client request {kind}")
        if kind == "session":
            self.session = True
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_publickey(self, username, key):
        if username == client_username and key == user_key:
            self.username = username
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED
    
    def check_auth_password(self, username, password):
        if password == client_password and username == client_username:
            self.username = username
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED
    
    def get_allowed_auths(self, username):
        return "password"


    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        print(f"client pty request on channel {channel}")
        return True

    def check_channel_shell_request(self, channel):
        print("shell request")
        self.shell_request = True
        self.subprocess = subprocess.Popen([shellpath], stdout=self.ptys, stdin=self.ptys, stderr=subprocess.STDOUT, shell=False)
        print(f"Open done, {self.subprocess}")
        return True

    def check_channel_exec_request(self, channel, command):
        print(f"exec request {command}")
        self.exec_request = True
        self.subprocess = subprocess.Popen([command], stdout=self.ptys, stdin=self.ptys, stderr=subprocess.STDOUT, shell=False)
        return True

def run():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((address, port))
    server_sock.setblocking(False)
    print("listening")
    server_sock.listen(100)

    await_clients = []
    all_clients = []

    while True:

        a, b, c = select.select([server_sock, ] + await_clients + all_clients, [], [], 0.1)
       
        for selected in a:
            if selected == server_sock:
                sock_client, addr = server_sock.accept()
                client = Client(sock_client, paramiko.Transport(sock_client, gss_kex=False))
                await_clients.append(client)
                print(f"New client from {addr}")
                
        for client in list(await_clients):
            if not client.channel:
                client.channel = client.transport.accept(0)
            if client.channel:
                if client.shell_request or client.exec_request:
                    await_clients.remove(client)
                    all_clients.append(client)
                    client.channel.send(f"Heisann, {client.username}!\r\n")

        for client in list(all_clients):
            if client.channel:
                if client.session:
                    retcode = None
                    if client.subprocess:
                        retcode = client.subprocess.poll()
                    if retcode != None:
                        #subprocess terminated, disconnect client.
                        client.channel.send(f"\r\nProcess terminated with code {retcode}\r\n")
                        client.channel.close()
                        all_clients.remove(client)
                        continue
                    stdin_data = None
                    if client.channel.recv_ready():
                        stdin_data = client.channel.recv(4096)
                        os.write(client.ptym, stdin_data)
                    try:
                        stdout_data = os.read(client.ptym, 4096)
                        client.channel.send(stdout_data)
                    except BlockingIOError:
                        pass

                        
                

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("--username", "-u", type=str, help="Specify login username",
                        default="azurediamond")
    parser.add_argument("--password", "-p",type=str,
                        help="Specify login password ('-' to read from stdin)",
                        default="hunter2")
    parser.add_argument("--listen", "-l", type=str, help="Listen address:port",
                        default="localhost:2200")
    parser.add_argument("--key","-k", type=str, help="Path to server key")
    parser.add_argument("--shell","-s", type=str, help="Path to shell", default="/bin/bash")
    
    args = parser.parse_args()
    if(args.password == "-"):
        client_password = input("Server password: ")
    else:
        client_password = args.password
    client_username = args.username
    port = int(args.listen.split(":")[-1])
    address = ":".join(args.listen.split(":")[:-1])

    if args.key is None:
        print("Please geneate an ECDSA host key and specify it using -k!")
        sys.exit(1)
        
    host_key = paramiko.ECDSAKey(filename=args.key)
    shellpath = args.shell
    run()

    
