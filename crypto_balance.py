import time, ethermine, pyetherbalance, coinbase # importing necessary packages
import RPi.GPIO as GPIO

from ethermine import Ethermine
from pyetherbalance import PyEtherBalance
from coinbase.wallet.client import Client

GPIO.setmode(GPIO.BOARD)

ethermine = Ethermine()
address = '0xec83bFA66dC39258eA1c2bA357E2014F6011eAa3' #0xec83bFA66dC39258eA1c2bA357E2014F6011eAa3
infura_url = 'https://mainnet.infura.io/v3/f3c59a8b19184092b483ba6fe5283b27'
ethbalance = pyetherbalance.PyEtherBalance(infura_url)
starttime = time.time()
refresh_timer = 60.0
stats = ethermine.miner_current_stats(address)
total = ethbalance.get_eth_balance(address)['balance'] + (stats['unpaid'] / 1000000000000000000)
coinbase_secret = 'FG5mKvtwbzQjjHJ1wm1wh2y77fA862Ob' #TODO finish coinbase implementation
coinbase_key = 'svpmwItmEYMxcgEF'
client = Client(coinbase_key, coinbase_secret)
price = client.get_sell_price(currency_pair = 'ETH-USD')['amount']
elapsedTime = 0.0
secPerCoin = 0.01
coinsPerSec = 0.00000001
unpaid = stats['unpaid'] / 1000000000000000000
avgHash = stats['averageHashrate'] / 1000000
print(total, " | ", unpaid)
print("Average Hashrate: ", str(round(avgHash,3)), " MH/s")

def update_avg_hashrate(): #function that updates the average
    stats = ethermine.miner_current_stats(address) # set stats to Object of miner's current stats
    price = client.get_sell_price(currency_pair = 'ETH-USD')['amount']
    global avgHash
    newHash = stats['averageHashrate'] / 1000000
    if newHash != avgHash:
        avgHash = stats['averageHashrate'] / 1000000
        print("Average Hashrate: ", str(round(avgHash,3)), " MH/s")

def update_per_min(): # updates the amount the user is mining per minute
    stats = ethermine.miner_current_stats(address)
    unpaid = stats['unpaid'] / 1000000000000000000
    global secPerCoin
    global coinsPerSec
    usdPerSec = stats['usdPerMin'] / 60.0
    coinsPerSec = stats['coinsPerMin'] / 60.0
    secPerCoin = 0.00000001 / coinsPerSec # 1 smallest eth division

try:
    while True:
    update_per_min()
    update_avg_hashrate()
    elapsedTime = 0.0
    while elapsedTime < 180.0: #update every 3 minutes
        total += 0.00000001
        #instead of the print statement below, this is where the LED updates would go
        print("Total: ", "{:.8f}".format(total), " | $", "{:.2f}".format((total * float(price))))
        time.sleep(secPerCoin - ((time.time() - starttime) % secPerCoin)) # sleep for small amount of time
        elapsedTime += secPerCoin
    difference = ethbalance.get_eth_balance(address)['balance'] - (total - (stats['unpaid'] / 1000000000000000000))
    print("Difference: ", "{:.9f}".format(difference), " ETH")
    total = ethbalance.get_eth_balance(address)['balance'] + (stats['unpaid'] / 1000000000000000000) # makes 'total' = the wallet balance + the unpaid

    ## TODO: average differences above and adjust ( if i feel like it and ever get around to it :p )
    ## TODO: it seems like the amount is resetting after every reset, check this and make sure the amount doesnt revert
except KeyboardInterrupt:
    GPIO.cleanup()
print("Exiting.")