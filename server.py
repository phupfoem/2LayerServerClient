from pickle import STRING
import sys
import socket
import threading
import pickle
import torch
import time
from random import seed
from random import randint
import argparse
from utils import print_msg
from DDP.model.model import NeuralNet


class Server:
    def __init__(self, port):
        seed(1)

        self.port = port
        self.socket = None
        self.client_conns = {}
        self.clients_responded = set()

        self.model = NeuralNet()
        self.sum = torch.zeros(self.model.fc.weight.shape)
        self.total_weight = 0
        self.seqnum = randint(0, 0xFFFF)

        self._key_lock = threading.Lock()

        self.set_up()

    def __del__(self):
        self.shut_down()

    def handle_request(self, client_conn, client_addr):
        """Handle request from clients."""
        while True:
            try:
                data_rcv = b''
                while True:
                    try:
                        data_rcv += client_conn.recv(4096)
                        data_rcv = pickle.loads(data_rcv)
                        break
                    except pickle.UnpicklingError:
                        pass

                print_msg("Received from " + client_addr + " " + str(data_rcv))

                if data_rcv == 'close':
                    self.remove_client(client_addr)
                    return

                if data_rcv is not None:
                    with self._key_lock:
                        seqnum = data_rcv['seqnum']
                        value = data_rcv['value']
                        weight = data_rcv['weight']

                        if seqnum != self.seqnum:
                            # Outdated, drop
                            continue

                        # Update attributes
                        self.clients_responded.add(client_addr)
                        self.sum += weight * value.data.clone()
                        self.total_weight += weight
                        print(weight)

                        # Reflect the change
                        print_msg("Current sum: " + str(self.sum))
                        print_msg("Current number of edges responded: "
                                  + str(len(self.clients_responded)))
                        print_msg("Current total weight: "
                                  + str(self.total_weight))
                        print_msg("------------------------------------")
                else:
                    self.remove_client(client_addr)
                    return
            except ConnectionError:
                self.remove_client(client_addr)
                return

    def send_to_client(self, data, client_conn, client_addr):
        """Send pickled data to the client."""
        try:
            client_conn.sendall(pickle.dumps(data))
        except (OSError, ConnectionError):
            client_conn.close()
            self.remove_client(client_addr)

    def broadcast_to_clients(self, data):
        """Send pickled data to all clients."""
        client_to_remove_addrs = []
        pickled_data = pickle.dumps(data)
        with self._key_lock:
            for addr, conn in self.client_conns.items():
                try:
                    conn.sendall(pickled_data)
                except (OSError, ConnectionError):
                    conn.close()
                    client_to_remove_addrs.append(addr)

        for addr in client_to_remove_addrs:
            self.remove_client(addr)

    def remove_client(self, client_addr):
        """Remove client connection."""
        with self._key_lock:
            try:
                # Update attributes
                try:
                    self.clients_responded.remove(client_addr)
                except KeyError:
                    pass

                self.client_conns.pop(client_addr)

                print_msg("Client " + client_addr + " disconnected.")
                print_msg("------------------------------------")
            except KeyError:
                pass

    def wait_for_clients(self):
        """Wait for clients' request for connection and provide worker thread
        serving the client.
        """
        while True:
            # Wait for client
            client_conn, (client_ip, client_port) = self.socket.accept()

            # The wait is done
            with self._key_lock:
                client_addr = client_ip + ":" + str(client_port)
                if client_addr in self.client_conns:
                    self.client_conns[client_addr].close()

                self.client_conns[client_addr] = client_conn

                print_msg(client_addr + " connected")
                print_msg("------------------------------------")

            self.send_to_client(
                {
                    'avg': self.model.fc.weight.data.clone(),
                    'seqnum': self.seqnum
                },
                client_conn,
                client_addr
            )

            # Provide worker thread to serve client
            worker_thread = threading.Thread(
                target=self.handle_request,
                args=(client_conn, client_addr)
            )
            worker_thread.daemon = True
            worker_thread.start()

    def broadcast_on_schedule(self):
        """Broadcast on schedule."""
        start_time = time.time()
        delay_time = 10.0
        max_delay = 30.0
        min_delay = 5.0
        while True:
            if len(self.client_conns) == 0:
                start_time = time.time()
            elif (
                time.time() - start_time > delay_time
                or len(self.clients_responded) == len(self.client_conns)
            ):
                with self._key_lock:
                    if self.total_weight == 0:
                        delay_time = min([delay_time * 2.0, max_delay])
                        start_time = time.time()
                        continue

                    if len(self.clients_responded) == len(self.client_conns):
                        delay_time = max([delay_time / 2.0, min_delay])
                    else:
                        delay_time = min([delay_time * 1.1, max_delay])

                    start_time = time.time()

                    self.clients_responded = set()
                    self.model.fc.weight.data = self.sum / self.total_weight
                    self.sum = torch.zeros(self.model.fc.weight.shape)
                    self.total_weight = 0
                    self.seqnum = randint(0, 0xFFFFFF)

                self.broadcast_to_clients({
                    'avg': self.model.fc.weight.data.clone(),
                    'seqnum': self.seqnum
                })

            time.sleep(0.1)

    def set_up(self):
        """Set up socket."""
        print_msg("Starting server.")

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.socket.bind(('', self.port))
        self.socket.listen(100)

        print_msg("Server started.")
        print_msg("------------------------------------")

    def run(self):
        """Call this method to run the server."""
        client_wait_thread = threading.Thread(
            target=self.wait_for_clients
        )
        client_wait_thread.daemon = True
        client_wait_thread.start()

        self.broadcast_on_schedule()

    def shut_down(self):
        """Properly shut down server."""
        print_msg("Shutting down server.")
        self.socket.close()


def main():
    # This is extended to allow flexible port number option
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default=30000, type=int, required= False, action='store')
    args = parser.parse_args()
    supposed_sys_argv = {
        'server.py': None,
        'port': args.port
    }

    # try:
    #     # Parsing command line arguments
    #     _, port = sys.argv
    #     port = int(port)
    # except ValueError:
    #     if len(sys.argv) > len(supposed_sys_argv):
    #         # Falling back to default values not possible
    #         # Print out usage syntax
    #         help_text = "[Usage: " + " ".join(supposed_sys_argv) + "\n"
    #         print(help_text)
    #         return

        # Defaulting
        # port = supposed_sys_argv['<port>']
    server = Server(supposed_sys_argv.get('port'))
    server.run()


if __name__ == '__main__':
    main()
