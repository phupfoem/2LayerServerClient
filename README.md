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
* change client_conns of internal_server to dictionary type
* update the value and remove the old value of the client being connected
* client_ip variable now includes the port with format: ip_add:port
* add __del__ to client