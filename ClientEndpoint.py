import grpc.aio

import jsonstore
import sys
import concurrent.futures
import asyncio
import takeorders_pb2_grpc
port_list = []
out_list = []


class Order():
    def __init__(self, port, order):
        self.responseMsgs = list()
        self.server_port = port
        self.order = order

    async def place_order(self):
        channel = grpc.aio.insecure_channel(f'localhost:{self.server_port}')
        stub = takeorders_pb2_grpc.OrderStub(channel)
        resp = await stub.SendOrder(self.order)
        self.responseMsgs.append(resp)


async def placeorders(orders):
    port, order = orders
    orderObj = Order(port,order)
    await orderObj.place_order()
    return orderObj


def start_async(portinlist):
    orderObj = asyncio.run(placeorders(portinlist))
    return orderObj.responseMsgs


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Missing arguments")
        exit()
    filename = sys.argv[1]
    orderlist = jsonstore.read_input(filename)

    port_list = list(jsonstore.read_portlist().values())
    in_list = zip(port_list, orderlist)

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futureresults = executor.map(start_async, in_list)
        for ascompleted in futureresults:
            out_list.append(ascompleted)

    print(f'Output from server --> {out_list}')

