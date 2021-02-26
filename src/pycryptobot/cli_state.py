class CLIState:
    def __init__(self):
        self._client = None
        self._account = None
        self.use_sandbox = False
        self.user = PROD_USER
        self.assume_yes = False

    @property
    def keys(self):
        return ApiKey(self.user)

    @property
    def client(self):
        if self._client is None:
            self._client = create_client(self.keys)
        return self._client

    @property
    def account(self):
        if self._account is None:
            self._account = Account(self.client, self.keys)
        return self._account

    def set_assume_yes(self, param):
        self.assume_yes = param

    def place_order(self, market, price, size, order_type, side):
        bookie = Bookie(self.client, market)
        return _get_response(lambda: bookie.place_order(price, size, order_type, side))

    def cancel_order(self, order_id):
        return _get_response(lambda: self.client.cancel_order(order_id))

    def get_order(self, order_id):
        return _get_response(lambda: self.client.get_order(order_id))

    def get_orders(self):
        return _get_response(lambda: self.client.get_orders())

    def get_fills(self, market):
        return _get_response(lambda: self.client.get_fills(product_id=market))