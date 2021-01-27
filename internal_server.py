import sys
import socket
import threading
import pickle
from utils import print_msg


class InternalServer:
    def __init__(self, upper_server_ip, upper_server_port, port):
        self.upper_server_ip = upper_server_ip
        self.upper_server_port = upper_server_port
        self.upper_server = None

        self.port = port
        self.socket = None
        self.client_conns = []
        self.sum = 0.0
        self.n_element = 0
        self.avg = 0.0

        self.set_up()

    def __del__(self):
        self.shut_down()

    def handle_request(self, client_conn, client_ip):
        """Handle request from clients."""
        while True:
            try:
                data_rcv = pickle.loads(client_conn.recv(1024))
                print_msg("Received from " + client_ip + " " + str(data_rcv))

                number = data_rcv
                if number:
                    # !!! Critical section
                    # Ok solely due to the module architecture

                    # Add number client sent to sum
                    self.sum += number
                    self.n_element += 1

                    # Calculate avg
                    self.avg = self.sum / self.n_element

                    # Reflect the change in sum and average
                    print_msg("Current sum: " + str(self.sum))
                    print_msg("Current average: " + str(self.avg))

                    # Calculate and send back to upper server
                    self.send_to_upper_server(self.avg)
                else:
                    self.remove_client(client_conn, client_ip)
                    return
            except (ConnectionError):
                self.remove_client(client_conn, client_ip)
                return
            except:
                print("Error handling client request.")

    def send_to_client(self, data, client_conn, client_ip):
        """Send pickled data to the client."""
        try:
            client_conn.send(pickle.dumps(data))
        except (OSError, ConnectionError):
            client_conn.close()
            self.remove_client(client_conn, client_ip)

    def broadcast_to_clients(self, data):
        """Send pickled data to all clients."""
        pickled_data = pickle.dumps(data)
        for conn in self.client_conns:
            try:
                conn.send(pickled_data)
            except (OSError, ConnectionError):
                conn.close()
                self.remove_client(conn)

    def remove_client(self, client_conn, client_ip=None):
        """Remove client connection."""
        try:
            self.client_conns.remove(client_conn)
        except ValueError:
            return

        if client_ip is not None:
            print_msg("Client " + client_ip + " disconnected.")

    def send_to_upper_server(self, data):
        """Send pickled data to upper server."""
        self.upper_server.send(pickle.dumps(data))

    def wait_for_clients(self):
        """Wait for clients' request for connection and provide worker thread
        serving the client.
        """
        while True:
            # Wait for client
            client_conn, (client_ip, _) = self.socket.accept()

            # Reflect the wait is done
            self.client_conns.append(client_conn)
            print_msg(client_ip + " connected")

            self.send_to_client(self.avg, client_conn, client_ip)

            # Provide worker thread to serve client
            worker_thread = threading.Thread(
                target=self.handle_request,
                args=(client_conn, client_ip)
            )
            worker_thread.daemon = True
            worker_thread.start()

    def wait_for_upper_server(self):
        """Wait receive new avg."""
        while True:
            # Receive input parameter from server
            data_rcv = pickle.loads(self.upper_server.recv(1024))
            print_msg("Received from upper server: " + str(data_rcv))

            # Make upper server's average as its own
            self.sum = self.avg = data_rcv
            self.n_element = 1

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

        self.wait_for_upper_server()

    def shut_down(self):
        """Properly shut down server."""
        print_msg("Shutting down server.")
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
