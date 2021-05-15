## Project details

The project uses the below main libraries and languages.
* Python 3.8.7 
* grpcio
* grpcio-tools
* Protobuf

1. Execute the command to run protobuf compiler to generate the Protobuf message file and Services or run `init.py`.  
   ``python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./takeorders.proto``
