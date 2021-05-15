import grpc
from concurrent import futures
import multiprocessing
import sys
import os
import socket
import jsonstore
import asyncio
from grpc_reflection.v1alpha import reflection
from grpc_health.v1 import health
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc
import StoreService
import takeorders_pb2
import takeorders_pb2_grpc

API_URL="http://localhost:8080"
API_KEY="secret_key"

def get_free_loopback_tcp_port():
    if socket.has_ipv6:
        tcp_socket = socket.socket(socket.AF_INET6)
    else:
        tcp_socket = socket.socket(socket.AF_INET)
    tcp_socket.bind(('', 0))
    address_tuple = tcp_socket.getsockname()
    tcp_socket.close()
    return address_tuple[1]


def server(server_id):
    sys.stdout.flush()
    port = get_free_loopback_tcp_port()
    bind_address = 'localhost:{}'.format(port)
    worker = multiprocessing.Process(target=launch_server_async,
                                     args=(bind_address, port, server_id),
                                     name=f'Server_{server_id}')
    worker.start()
    return port


def launch_server_async(bind_address, port, server_id):
    asyncio.run(launch_server(bind_address, port, server_id))


async def launch_server(bind_address, port, server_id):
    """Start async grpcio server sub process"""
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=5, ))
    takeorders_pb2_grpc.add_OrderServicer_to_server(StoreService.Store(server_id, port, API_URL, API_KEY), server)

    health_servicer = health.HealthServicer(experimental_non_blocking=True,
                                            experimental_thread_pool=futures.ThreadPoolExecutor(max_workers=1))
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    services = tuple(service.full_name for service in takeorders_pb2.DESCRIPTOR.services_by_name.values()) \
               + (reflection.SERVICE_NAME, health.SERVICE_NAME)
    reflection.enable_server_reflection(services, server)
    server.add_insecure_port(bind_address)

    await server.start()

    # Mark all services as healthy.
    overall_server_health = ""
    for service in services + (overall_server_health,):
        health_servicer.set(service, health_pb2.HealthCheckResponse.SERVING)
    await server.wait_for_termination()


def launch_servers():
    portList = {i: server(i) for i in range(1, multiprocessing.cpu_count() + 1)}
    return portList


if __name__ == '__main__':
    portList = launch_servers()
    status = jsonstore.writeserverports(portList)
    if status is True:
        print("Launched servers successfully")
    else:
        print("Launching servers failed")
