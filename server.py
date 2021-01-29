import sys
import socket
import threading
import pickle
from utils import print_msg


class Server:
    def __init__(self, port):
        self.port = port
        self.socket = None
        self.client_conns = {}
        self.sum = 0.0
        self.n_element = 0
        self.avg = 0.0
        self.n_client = 0

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
                if number == "close":
                    self.remove_client(client_conn, client_ip)
                    return
                if number:
                    # !!! Critical section
                    # Ok solely due to the module architecture

                    # Add number to db
                    old_number = self.client_conns[client_ip][1]
                    old_num_of_clients = self.client_conns[client_ip][2]
                    self.client_conns[client_ip][1] = number[0]
                    self.client_conns[client_ip][2] = number[1]

                    self.n_client -= old_num_of_clients
                    self.n_client += number[1]

                    # Add number client sent to sum
                    self.sum -= old_number*old_num_of_clients
                    self.sum += number[0]*number[1]

                    # Calculate avg
                    print(self.sum)
                    print(self.n_client)
                    self.avg = self.sum / self.n_client

                    # Reflect the change in sum and average
                    print_msg("Current sum: " + str(self.sum))
                    print_msg("Current average: " + str(self.avg))
                    print_msg("Current number of edges: " + str(self.n_element))
                    print_msg("Current total clients: " + str(self.n_client))
                    print_msg("------------------------------------")

                    # Calculate and send back to all clients
                    self.broadcast_to_clients(self.avg)
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
        for ip, lis in self.client_conns.items():
            try:
                lis[0].send(pickled_data)
            except (OSError, ConnectionError):
                lis[0].close()
                self.remove_client(lis[0])

    def remove_client(self, client_conn, client_ip=None):
        """Remove client connection."""
        length = len(self.client_conns)

        data_in_this_edge = 0
        number_of_client_in_this_edge = 0
        temp = {}
        for key, value in self.client_conns.items():
            if value[0] != client_conn:
                temp[key] = value
            else:
                data_in_this_edge = value[1]
                number_of_client_in_this_edge = value[2]
        self.client_conns = temp

        if length == len(self.client_conns):
            return

        self.sum -= data_in_this_edge
        self.n_client -= number_of_client_in_this_edge
        self.n_element -= 1

        if client_ip is not None:
            print_msg("Client " + client_ip + " disconnected.")

    def wait_for_clients(self):
        """Wait for clients' request for connection and provide worker thread
        serving the client.
        """
        while True:
            # Wait for client
            client_conn, (client_ip, client_port) = self.socket.accept()

            # Reflect the wait is done
            client_ip = client_ip + ":" + str(client_port)
            if client_ip in self.client_conns:
                self.client_conns[client_ip][0].close()
                self.n_element -= 1
            self.client_conns[client_ip] = []
            self.client_conns[client_ip].append(client_conn)
            # init the value of the client
            self.client_conns[client_ip].append(0)  # number that edge send
            self.client_conns[client_ip].append(0)  # number of clients connected with edge
            self.n_element += 1
            print_msg(client_ip + " connected")

            self.send_to_client(self.avg, client_conn, client_ip)

            # Provide worker thread to serve client
            worker_thread = threading.Thread(
                target=self.handle_request,
                args=(client_conn, client_ip)
            )
            worker_thread.daemon = True
            worker_thread.start()

    def set_up(self):
        """Set up socket."""
        print_msg("Starting server.")

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.socket.bind(('', self.port))
        self.socket.listen(100)

        print_msg("Server started.")

    def run(self):
        """Call this method to run the server."""
        self.wait_for_clients()

    def shut_down(self):
        """Properly shut down server."""
        print_msg("Shutting down server.")
        self.socket.close()


def main():
    # This is extended to allow flexible port number option
    supposed_sys_argv = {
        'server.py': None,
        '<port>': 4000
    }

    try:
        # Parsing command line arguments
        _, port = sys.argv
        port = int(port)
    except ValueError:
        if len(sys.argv) > len(supposed_sys_argv):
            # Falling back to default values not possible
            # Print out usage syntax
            help_text = "[Usage: " + " ".join(supposed_sys_argv) + "\n"
            print(help_text)
            return

        # Defaulting
        port = supposed_sys_argv['<port>']

    server = Server(port)
    server.run()


if __name__ == '__main__':
    main()
