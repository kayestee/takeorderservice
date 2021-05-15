import threading
import grpc
import takeorders_pb2
import takeorders_pb2_grpc
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


class Store(takeorders_pb2_grpc.OrderServicer):
    def __init__(self, id, port, stockCount):
        self.id = id
        self.port = port
        self.lock = threading.Lock()
        self.stockCount = stockCount

    async def SendOrder(self, request, context):
        print(f'Execute {request.action} at Server {self.id} ')
        if request.action == "placeorder":
            resp = await self.ConfirmOrder(request, context)
        return resp

    async def ConfirmOrder(self, request, context):
        orderRes = takeorders_pb2.MessageReply(id=self.id)
        try:
            for item in request.items:
                self.update_stock(item.item_qty)
                orderRes.itemResp.append(takeorders_pb2.ItemStatus(itemId=item.item_id, wasPlaced="Y"))
                print(orderRes)
        except:
            orderRes = takeorders_pb2.MessageReply(id=self.id, orderStatus="Failed")

        return orderRes

    async def TakeStock(self, request, context):
        try:
            self.lock.acquire(blocking=True)
            stock = self.stockCount
        finally:
            self.lock.release()
        response = takeorders_pb2.OrderStockMsg(id=self.id, status="Success")
        return response


    def update_stock(self, stockQty):
        try:
            self.lock.acquire(blocking=True)
            self.stockCount = self.stockCount - stockQty
        finally:
            self.lock.release()


def get_free_loopback_tcp_port():
    if socket.has_ipv6:
        tcp_socket = socket.socket(socket.AF_INET6)
    else:
        tcp_socket = socket.socket(socket.AF_INET)
    tcp_socket.bind(('', 0))
    address_tuple = tcp_socket.getsockname()
    tcp_socket.close()
    return address_tuple[1]


def server(server_id, port):
    sys.stdout.flush()
    workers = []
    bind_address = 'localhost:{}'.format(port)
    worker = multiprocessing.Process(target=launch_server_async,
                                     args=(bind_address, port, server_id),
                                     name=f'Server_{server_id}')
    workers.append(worker)
    worker.start()
    return worker.pid


def launch_server_async(bind_address, port, server_id):
    asyncio.run(launch_server(bind_address, port, server_id))


async def launch_server(bind_address, port, server_id):
    """Start async grpcio server sub process"""
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=5, ))
    takeorders_pb2_grpc.add_OrderServicer_to_server(Store(server_id, port, 10000), server)

    health_servicer = health.HealthServicer(experimental_non_blocking=True,
                                            experimental_thread_pool=futures.ThreadPoolExecutor(max_workers=1))
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer,server)
    services = tuple(service.full_name for service in takeorders_pb2.DESCRIPTOR.services_by_name.values()) \
               + (reflection.SERVICE_NAME, health.SERVICE_NAME)
    reflection.enable_server_reflection(services,server)
    server.add_insecure_port(bind_address)

    await server.start()

    # Mark all services as healthy.
    overall_server_health = ""
    for service in services + (overall_server_health,):
        health_servicer.set(service, health_pb2.HealthCheckResponse.SERVING)
    await server.wait_for_termination()


def launch_servers(cpucount):
    portList = {}
    for  i in range(1,cpucount+1):
        port = get_free_loopback_tcp_port()
        portList[i] = port
        server(i, port)
    return portList


if __name__ == '__main__':
    portList = launch_servers(os.cpu_count())
    print(portList)
    status = jsonstore.write_portlist(portList)
    if status is True:
        print("Launched servers successfully")
    else:
        print("Launching servers failed")
