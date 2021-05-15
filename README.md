## Project details

The project implements the solution using
* Python 3.8.7 
* grpcio
* Google Protobuf

1. Execute the command to run protobuf compiler to generate the Protobuf message file and Services or run `init.py`.  
   ``python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./takeorders.proto``
