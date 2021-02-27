import json
from pycryptobot.models.trading_account import TradingAccount

with open('config.json') as config_file:
    config = json.load(config_file)

account = TradingAccount(config)

print (account.get_balance())
#print (account.getBalance('BTC'))

#print (account.getOrders('BTC-GBP', '', 'done'))

#account.saveTrackerCSV()
#account.saveTrackerCSV('BTC-GBP')
#account.saveTrackerCSV('BTC-GBP', 'outputfile.csv')