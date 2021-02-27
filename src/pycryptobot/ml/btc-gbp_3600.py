import sys
import pandas as pd

sys.path.append(".")
# pylint: disable=import-error
from pycryptobot.models.trading import TechnicalAnalysis
from pycryptobot.models.coinbase_pro import PublicAPI

api = PublicAPI()
data = api.getHistoricalData("BTC-GBP", 3600)

ta = TechnicalAnalysis(data)
ta.addAll()

df = ta.getDataFrame()
df.to_csv("ml/data/BTC-GBP_3600.csv", index=False)
