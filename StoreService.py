import takeorders_pb2
import takeorders_pb2_grpc
import requests


class Store(takeorders_pb2_grpc.OrderServicer):
    def __init__(self, id, port, url, key):
        self.id = id
        self.port = port
        self.DB_API_URL = url
        self.DB_API_KEY = key


    async def SendOrder(self, request, context):
        if request.action == "placeorder":
            resp = await self.ConfirmOrder(request, context)
        return resp

    async def ConfirmOrder(self, request, context):
        orderRes = takeorders_pb2.MessageReply(id=self.id)
        try:
            for item in request.items:
                # updateR = self.update_stock(item)
                orderRes.itemResp.append(takeorders_pb2.ItemStatus(itemId=item.item_id, currentState="Y"))
        except:
            orderRes = takeorders_pb2.MessageReply(id=self.id, orderStatus="Failed")
        print(orderRes)
        return orderRes

    async def TakeStock(self, request, context):
        try:
            stockResp = takeorders_pb2.OrderStatusResp(id=self.id, orderStatus="Success")

            params = {'api_key': self.DB_API_KEY, 'order_id': request.item_id, 'customer_email': request.item_qty}
            resp = requests.get(url=f'{self.DB_API_URL}/getorder', data=params)
            resp.raise_for_status()
            if resp.status_code == 200:
                return stockResp
        except requests.exceptions.HTTPError:
            response = takeorders_pb2.OrderStatusResp(id=self.id, orderStatus="Failed")
            return response


    def update_stock(self, item):
        try:
            params = {'api_key': self.DB_API_KEY, 'item_id': item.item_id, 'item_qty': item.item_qty}
            resp = requests.post(url=f'{self.DB_API_URL}/confirmorder', data=params)
            resp.raise_for_status()
            if resp.status_code == 200:
                return resp
        except requests.exceptions.HTTPError:
            print(requests.exceptions.HTTPError)

