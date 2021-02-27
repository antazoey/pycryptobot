from pycryptobot.config import ConfigParser
from pycryptobot.models.trading_account import TradingAccount


class SupportingModels:
    def __init__(self):
        self._config = None

    @property
    def config(self):
        if self._config is None:
            config = ConfigParser()
            config.load_from_local_file()
            self._config = config
        return self._config

    @property
    def account(self):
        if self.account is None:
            config = self.config
            self.account = TradingAccount(config)
        return self.account
