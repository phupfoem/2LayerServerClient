import sys
import socket
import random
import select
from datetime import datetime


class Client:
    def __init__(self, host_ip, host_port):
        self.host_ip = host_ip
        self.host_port = host_port
        self.server = None
        self.firt_time = True

    def print_msg(self, msg):
        current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print('[' + str(current_date_time) + '] ' + msg)

    def configure_client(self):
        self.print_msg('Creating UDP/IPv4 socket ...')
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((self.host_ip, self.host_port))

    def communicate_with_server(self):
        # Send a random number to server and receive info
        print("Type any to send number to server")
        while True:
            socket_list = [sys.stdin, self.server]
            # print("Type any to send number to server")
            read_sockets, _, _ = select.select(socket_list, [], [])
            for sockets in read_sockets:
                if sockets == self.server:
                    # Receive number
                    recv_msg = sockets.recv(1024)
                    self.print_msg('Received from server: ' + str(recv_msg.decode('utf-8')))
                else:
                    input("")
                    print("Typed to send number to server")
                    num_to_send = str(round(random.uniform(0.1, 999.999), 6))
                    self.server.send(num_to_send.encode('utf-8'))
                    self.print_msg('Sent number: ' + str(num_to_send))


def main():
    if len(sys.argv) != 3:
        print("Correct usage: client.py <IP address> <port number>")
        exit()
    host_ip = str(sys.argv[1])
    host_port = int(sys.argv[2])
    client = UDPClient(host_ip, host_port)
    client.configure_client()
    client.communicate_with_server()


if __name__ == '__main__':
    main()
