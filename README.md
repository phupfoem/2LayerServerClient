# Edge Networking for Federated Learning

This project is conducted by staff and students of Ho Chi Minh City University of Technology, Vietnam National University Ho Chi Minh City.
Members:\
Supervisor: Thinh Q. Dinh, Ph.D\
Students:\
[Phu H. T. Nguyen](https://github.com/phupfoem)\
[Tung K. Tran](https://github.com/KhanhTungTran)

Federated Learning (FL) is an emerging paradigm allowing training machine learning models without centralized collecting user data and training models in cloud servers unlike conventional machine learning systems. Iteratively, local models are learned at mobile users, then aggregated at a cloud server, and continued to be updated by local data based on the aggregated model. Thus, this scheme protects user privacy and leverages the computing of local clients. However, current FL systems using server-clients models suffer a great burden of traffic and computing at the cloud server. Thus, in this project, we propose a two-tier edge network solution which can offload the traffic and computing load from the cloud node to edge nodes."

## Demo:
*Need other settings from other modules before doing this*\
*Run backend, frontend, mongodb first*

Then, on the machine intended to be made into the top-level server, run:\
**python server.py \<server_port\>**

Likewise, on edge devices, run:\
**python edge_server.py *\<server_ip\> \<server_port\> \<edge_port\>***

Finally, clients can connect to the edge device of choice by running:\
**python client.py *\<edge_ip\> \<edge_port\>***

## Changelog:
**Update client, edge**
* change client_conns of internal_server to dictionary type
* update the value and remove the old value of the client being connected
* client_ip variable now includes the port with format: ip_add:port
* add __del__ to client

**Update server, edge**
* change the data type that send from internal to server
* change the way that server and edge calculate the sum and average value
* knowned issue: the server and the edge should not run in the IDE terminal in order to shutdown them normally

**Solve critical section problem**
* solved issue: when deletes an client, the sum value of the server cannot change immediately


## Note
- [solve async problem](https://stackoverflow.com/questions/52133031/receiving-async-error-when-trying-to-import-the-firebase-package)
