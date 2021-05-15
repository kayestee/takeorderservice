import json
from google.protobuf import json_format
import takeorders_pb2


def read_input(path):
    orderlist = []
    with open(path) as input_json:
        for item in json.load(input_json):
            order = json_format.ParseDict(js_dict=item, message=takeorders_pb2.OrderMessage())
            orderlist.append(order)
    return orderlist


def writeserverports(ports):
    with open('ports.json', 'w') as file:
        json.dump(ports, file)
        return True


def readserverports():
    ports = []
    with open('ports.json') as file:
        ports = json.load(file)
    return ports