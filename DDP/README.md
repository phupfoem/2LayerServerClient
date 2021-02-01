# Distributed data parallel for Neural network training

This is a basic repository for demonstration on how to take advantage of multi-machines for distributed data parallel (DDP) training on a Neural network.

The implementation is based on *Pytorch*, specificially the module *torch.nn.parallel.DistributedDataParallel*: 
>"This container parallelizes the application of the given module by splitting the input across the specified devices by chunking in the batch dimension. The module is replicated on each machine and each device, and each such replica handles a portion of the input. During the backwards pass, gradients from each node are averaged."



## Frontend
First of all, you need to install Node.js which can be found at https://nodejs.org/en/

Second, in the terminal, change dir to frontend folder and run command:
```
npm install
```
to install all dependencies, and then run
```
npm start
```

## Backend
Regarding of backend, you need to install mongo database, which can be found at https://www.mongodb.com/try/download/community

Then, in the terminal, change dir to backend folder and run command:
```
npm install
```
to install all dependencies, and then run
```
npm start
```
to start the server. Moreover, you can see the database via the GUI MongoDBCompass included in the downloaded mongodb package
## Model
```
Please read Readme in model directory for more information
```

## Project status and Roadmap
**TODO list:**
- Create a GUI to choose which model will be used
- Make it work on an network

## Author
Current author: 
- [Tran Khanh Tung](https://github.com/KhanhTungTran)
- [Tran Hoang Viet](https://github.com/HoangViet144)

## References
- [Distributed data parallel training in Pytorch](https://yangkky.github.io/2019/07/08/distributed-pytorch-tutorial.html)
- [DISTRIBUTED DATA PARALLEL](https://pytorch.org/docs/master/notes/ddp.html)
- [React JS](https://reactjs.org)
