# Edge Networking for Federated Learning

This project is conducted by staff and students of Ho Chi Minh City University of Technology, Vietnam National University Ho Chi Minh City.

Members:
* Supervisor: Thinh Q. Dinh, Ph.D
* Students:\
[Phu H. T. Nguyen](https://www.linkedin.com/in/ph%C3%BA-nguy%E1%BB%85n-86a980200/)\
[Tung K. Tran](https://github.com/KhanhTungTran)\
[Viet H. Tran](https://github.com/HoangViet144)\
[Phat T. Hoang](https://github.com/hoangphatmonter)\
[Son Le-Thanh](https://github.com/sonLe-Thanh)\
[Viet H. Nguyen](https://github.com/vietnguyen2000)

Federated Learning (FL) is an emerging paradigm allowing training machine learning models without centralized collecting user data and training models in cloud servers unlike conventional machine learning systems. Iteratively, local models are learned at mobile users, then aggregated at a cloud server, and continued to be updated by local data based on the aggregated model. Thus, this scheme protects user privacy and leverages the computing of local clients. However, current FL systems using server-clients models suffer a great burden of traffic and computing at the cloud server. Thus, in this project, we propose a two-tier edge network solution which can offload the traffic and computing load from the cloud node to edge nodes.

## Demo:
*You need other settings from other modules before doing this*\
*First, run backend, frontend, mongodb as written in the readme files in those module folders.*

Then, on the machine intended to be made into the top-level server, run:
```
python server.py <server_port>
```

Likewise, on edge devices, run:
```
python edge_server.py <server_ip> <server_port> <edge_port>
```

Finally, clients can connect to the edge device of choice by running:
```
python client.py <edge_ip> <edge_port>
```
