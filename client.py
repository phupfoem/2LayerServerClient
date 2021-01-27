import sys
import socket
import pickle
import random
import time
from utils import print_msg


class Client:
    def __init__(
        self,
        host_ip,
        host_port,
        # Below generator is a placeholder that takes 5 seconds to complete
        num_gen=lambda _: [random.uniform(0.1, 999.999), time.sleep(5)][0]
    ):
        self.host_ip = host_ip
        self.host_port = host_port
        self.server = None
        self.num_gen = num_gen

        self.set_up()

    def communicate_with_server(self):
        """Generate & send a number to server & receive new input parameter."""
        while True:
            # Receive input parameter from server
            data_rcv = pickle.loads(self.server.recv(1024))
            print_msg('Received from server: ' + str(data_rcv))

            # Generate new number
            num = self.num_gen(data_rcv)
            print_msg('Sent number: ' + str(num))

            # Send number back to server
            data_to_send = pickle.dumps(num)
            self.server.send(data_to_send)

    def set_up(self):
        """Set up connection with server"""
        print_msg('Creating UDP/IPv4 socket ...')

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((self.host_ip, self.host_port))

    def run(self):
        """Call this method to run the client app."""
        self.communicate_with_server()
        


def main():
    # This is extended to allow default server socket
    supposed_sys_argv = {
        'client_launcher.py': None,
        '<server_ip>': 'localhost',
        '<server_port>': 4000
    }

    try:
        # Parsing command line arguments
        _, server_ip, server_port = sys.argv
        server_port = int(server_port)
    except ValueError:
        if len(sys.argv) > len(supposed_sys_argv):
            # Falling back to default values not possible
            # Print out usage syntax
            help_text = "[Usage: " + " ".join(supposed_sys_argv) + "\n"
            print(help_text)
            return

        # Defaulting
        server_ip = supposed_sys_argv['<server_ip>']
        server_port = supposed_sys_argv['<server_port>']

    client = Client(server_ip, server_port)
    client.run()


if __name__ == '__main__':
    main()
