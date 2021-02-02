import sys
import socket
import threading
import pickle
import torch
import time

from utils import print_msg
from DDP.model.model import NeuralNet


class InternalServer:
    def __init__(self, upper_server_ip, upper_server_port, port):
        self.upper_server_ip = upper_server_ip
        self.upper_server_port = upper_server_port
        self.upper_server = None

        self.port = port
        self.socket = None
        self.client_conns = {}
        self.clients_responded = set()

        self.model = NeuralNet()
        self.sum = torch.zeros(self.model.fc.weight.shape)
        self.total_weight = 0
        self.seqnum = -1

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

    def send_to_upper_server(self, data):
        """Send pickled data to upper server."""
        print_msg("Sent data: " + str(data))
        self.upper_server.sendall(pickle.dumps(data))
        print_msg("------------------------------------")

    def send_to_upper_server_on_schedule(self):
        """Send to upper server on schedule."""
        start_time = time.time()
        delay_time = 5.0
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
                        delay_time = min([delay_time + 1.0, max_delay])
                        continue

                    if len(self.clients_responded) == len(self.client_conns):
                        delay_time = max([delay_time / 2.0, min_delay])

                    self.clients_responded = set()
                    self.model.fc.weight.data = self.sum / self.total_weight
                    self.sum = torch.zeros(self.model.fc.weight.shape)
                    old_weight = self.total_weight
                    self.total_weight = 0

                self.send_to_upper_server({
                    'value': self.model.fc.weight.data.clone(),
                    'weight': old_weight,
                    'seqnum': self.seqnum
                })

            time.sleep(delay_time / 10)

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

    def wait_for_upper_server(self):
        """Wait receive new avg."""
        while True:
            # Receive input parameter from server
            data_rcv = b''
            while True:
                try:
                    data_rcv += self.upper_server.recv(4096)
                    data_rcv = pickle.loads(data_rcv)
                    break
                except pickle.UnpicklingError:
                    pass

            print_msg("Received from upper server: " + str(data_rcv))
            print_msg("------------------------------------")

            with self._key_lock:
                self.model.fc.weight.data = data_rcv['avg'].data.clone()
                self.sum = torch.zeros(self.model.fc.weight.shape)
                self.total_weight = 0
                self.seqnum = data_rcv['seqnum']

            # Send number to all clients
            self.broadcast_to_clients(data_rcv)

    def set_up(self):
        """Set up socket and connection to server."""
        self.set_up_socket()
        self.set_up_conn_to_upper_server()

    def set_up_socket(self):
        """Set up socket."""
        print_msg("Starting server.")

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.socket.bind(('', self.port))
        self.socket.listen(100)

        print_msg("Server started.")
        print_msg("------------------------------------")

    def set_up_conn_to_upper_server(self):
        """Set up connection to server."""
        print_msg("Creating connection to upper server")

        self.upper_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.upper_server.connect(
            (self.upper_server_ip, self.upper_server_port)
        )

        print_msg("Connection established")

    def run(self):
        """Call this method to run the server."""
        server_thread = threading.Thread(
            target=self.wait_for_clients
        )
        server_thread.daemon = True
        server_thread.start()

        client_thread = threading.Thread(
            target=self.wait_for_upper_server
        )
        client_thread.daemon = True
        client_thread.start()

        self.send_to_upper_server_on_schedule()

    def shut_down(self):
        """Properly shut down server."""
        print_msg("Shutting down server.")

        data_to_send = pickle.dumps('close')
        self.socket.sendall(data_to_send)

        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()


def main():
    # This is extended to allow flexible port number option
    supposed_sys_argv = {
        'internal_server.py': None,
        '<upper_server_ip>': 'localhost',
        '<upper_server_port>': 4000,
        '<port>': 4001
    }

    try:
        # Parsing command line arguments
        _, upper_server_ip, upper_server_port, port = sys.argv
        upper_server_port = int(upper_server_port)
        port = int(port)
    except ValueError:
        if len(sys.argv) > len(supposed_sys_argv):
            # Falling back to default values not possible
            # Print out usage syntax
            help_text = "[Usage: " + " ".join(supposed_sys_argv) + "\n"
            print(help_text)
            return

        # Defaulting
        upper_server_ip = supposed_sys_argv['<upper_server_ip>']
        upper_server_port = supposed_sys_argv['<upper_server_port>']
        port = supposed_sys_argv['<port>']

    server = InternalServer(upper_server_ip, upper_server_port, port)
    server.run()


if __name__ == '__main__':
    main()
