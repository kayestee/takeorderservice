import json
from google.protobuf import json_format
import takeorders_pb2


def read_input(path):
    orderlist = []
    with open(path) as input_json:
        for item in json.load(input_json):

            # order = json_format.Parse(text=json.dumps(item), message=takeorders_pb2.OrderMessage())
            order = json_format.ParseDict(js_dict=item, message=takeorders_pb2.OrderMessage())
            orderlist.append(order)
    return orderlist


def write_output(results):
    with open('output.json', 'w') as file:
        for result in results:
            file.writelines(json_format.MessageToJson(result))
        return 1


def write_portlist(ports):
    with open('portlist.json', 'w') as file:
        print(ports)
        json.dump(ports, file)
        return True


def read_portlist():
    portlist = []
    with open('portlist.json') as file:
        portlist = json.load(file)
    return portlist