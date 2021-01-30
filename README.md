# Multi-layer server client system

Currently works for 2-layer client-server interaction.

## WIP:
* Failsafe mechanism (i.e. unexpected crash of server(s))
* Sensible averaging algorithm
* Capability to send large files over socket

## Demo:
**python server.py**\
**python internal_server.py**\
**python client.py**

## Changelog:
**Update client, edge**\
* change client_conns of internal_server to dictionary type
* update the value and remove the old value of the client being connected
* client_ip variable now includes the port with format: ip_add:port
* add __del__ to client

**Update server, edge**\
* change the data type that send from internal to server
* change the way that server and edge calculate the sum and average value
* knowned issue: the server and the edge should not run in the IDE terminal in order to shutdown them normally

**Solve critical section problem**\
* solved issue: when deletes an client, the sum value of the server cannot change immediately