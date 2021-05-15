from grpc_tools import protoc

if __name__ == '__main__':
    args = ['grpc_tools.protoc', '-I.', '--python_out=.', '--grpc_python_out=.', './takeorders.proto']
    protoc.main(args)