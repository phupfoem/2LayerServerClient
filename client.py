import sys
import socket
import pickle
import threading
import time
import argparse
import torch
import torchvision

from utils import print_msg
from DDP.model.model import NeuralNet


class Client:
    def __init__(
        self,
        server_ip,
        server_port
    ):
        self.server_ip = server_ip
        self.server_port = server_port
        self.server = None

        self.model = NeuralNet()

        # attribute for train method only
        self.optimizer = torch.optim.SGD(self.model.parameters(), 0.0001)
        self.criterion = torch.nn.CrossEntropyLoss()
        self.ds = torchvision.datasets.MNIST(
            root='./data',
            transform=torchvision.transforms.ToTensor()
        )
        self.dl = torch.utils.data.DataLoader(
            dataset=self.ds,
            batch_size=100,
            shuffle=False
        )

        self.server_avg = torch.zeros(self.model.fc.weight.shape)
        self.seqnum = -1

        self._key_lock = threading.Lock()

        self.set_up()

        #statistic
        self.startSendTime = time.time()
        self.latency = 0

    def __del__(self):
        self.shut_down()

    def wait_for_server(self):
        """Receive new avg and update accordingly."""
        while True:
            # Receive input parameter from server
            data_rcv = b''
            while True:
                try:
                    data_rcv += self.server.recv(4096)
                    self.latency = time.time() - self.startSendTime
                    data_rcv = pickle.loads(data_rcv)
                    break
                except pickle.UnpicklingError:
                    pass
            
            # print_msg("Received from server: " + str(data_rcv))
            print_msg("Reply from ip:"+ str(self.server_ip) + " port: "+ str(self.server_port) +" : time="+  str(int(self.latency*1000)) +" ms")
            print_msg("------------------------------------")

            with self._key_lock:
                self.server_avg = data_rcv['avg'].data.clone()
                self.seqnum = data_rcv['seqnum']

    def send_to_server(self, data):
        """Send pickled data to server."""
        print_msg("Sent data: " + str(data))
        self.startSendTime = time.time()
        self.server.sendall(pickle.dumps(data))
        print_msg("------------------------------------")

    def train(self):
        with self._key_lock:
            old_seqnum = self.seqnum

        while True:
            if old_seqnum == self.seqnum:
                time.sleep(0.1)
                continue

            with self._key_lock:
                self.model.fc.weight.data = self.server_avg.data.clone()
                self.model.train()

            train_loss = 0.0

            for i, (data, target) in enumerate(self.dl):
                if i > 100:
                    break

                with self._key_lock:
                    output = self.model(data)
                    loss = self.criterion(output, target)
                    self.optimizer.zero_grad()
                    loss.backward()
                    self.optimizer.step()

                    train_loss += loss.item() / len(self.dl)

            print_msg("Current loss value: " + str(train_loss))
            print_msg("------------------------------------")

            # Send avg to server
            self.send_to_server({
                'value': self.model.fc.weight.data.clone(),
                'weight': 1,
                'seqnum': self.seqnum
            })

            old_seqnum = self.seqnum

    def set_up(self):
        """Set up connection with server"""
        print_msg("Creating connection to server")

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.startSendTime = time.time()
        self.server.connect((self.server_ip, self.server_port))

        print_msg("Connection established")
        print_msg("------------------------------------")

    def run(self):
        """Call this method to run the client app."""
        train_thread = threading.Thread(
            target=self.train
        )
        train_thread.daemon = True
        train_thread.start()

        self.wait_for_server()

    def shut_down(self):
        """Properly shut down client."""
        print_msg("Shutting down socket in client")

        data_to_send = pickle.dumps('close')
        self.server.sendall(data_to_send)

        self.server.shutdown(socket.SHUT_RDWR)
        self.server.close()


def main():
    # This is extended to allow default server socket
    parser = argparse.ArgumentParser()
    parser.add_argument('--server_port', default=40000, type=int, metavar='N')
    args = parser.parse_args()
    supposed_sys_argv = {
        'client.py': None,
        'server_ip': 'localhost',
        'server_port': args.server_port
    }

    # try:
    #     # Parsing command line arguments
    #     _, server_ip, server_port = sys.argv
    #     server_port = int(server_port)
    # except ValueError:
    #     if len(sys.argv) > len(supposed_sys_argv):
    #         # Falling back to default values not possible
    #         # Print out usage syntax
    #         help_text = "[Usage: " + " ".join(supposed_sys_argv) + "\n"
    #         print(help_text)
    #         return

    #     # Defaulting
    #     server_ip = supposed_sys_argv['<server_ip>']
    #     server_port = supposed_sys_argv['<server_port>']

    client = Client(supposed_sys_argv.get('server_ip') ,supposed_sys_argv.get('server_port') )
    client.run()


if __name__ == '__main__':
    main()
