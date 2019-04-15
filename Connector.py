import hashlib
import urllib.parse
import time
import hmac
import requests

'''Работа с API бирж, задача - сделать универсальный коннектор'''


class AllExchange:
    def __init__(self, api_key=None, secret=None):
        self.api_key = api_key
        self.secret = secret

    def all_ticker_name(self, proxy):
        pass

    def ticker_price(self, symbol, proxy):
        pass

    # cid - for select right api/secret keys
    def orders_list(self, cid, symbol):
        pass

    def create_order(self, cid):
        pass

    @staticmethod
    def hash_creator(secret, payload: dict, code_sha: str, url=None):
        sha = {'256': hashlib.sha256,
               '512': hashlib.sha512}.get(code_sha)
        # кодируем параметры строки запроса в байт строку
        param = urllib.parse.urlencode(payload)#.encode('utf-8')
        # добавляем параметры запроса к адресу endpoint
        if url is None:  # обработка из-за Binance
            url = param
        else:
            url += param
        # создаем подпись для запроса
        sign = hmac.new(secret, url.encode('utf-8'), sha).hexdigest()
        return sign

# ==============================BINANCE=================================================================================


class Binance(AllExchange):
    @staticmethod
    def pretty_data(data):
        ticker_name = []
        if isinstance(data, dict):
            return data.get('price')
        for tickerprice in data:
            ticker_name.append(tickerprice['symbol'])
        return ticker_name

    @staticmethod
    def data_encrypter():
        api = b'rdydTXwFlP4PISVAZnottruetU7qH8qj0UO9aG6hVZacxNGntlzl3ECPBpUivZ'
        secret = b'iDCP4Mm92un9as8nottrueqV2I6pSFKVqtW2gQJMor20fmVdIoKufSKaU4Y2wwfkG'
        return {'api_key': api,
                'secret': secret}

    def all_ticker_name(self, proxy):
        url = 'https://api.binance.com/api/v3/ticker/price'
        resp = requests.get(url)
        return Binance.pretty_data(resp.json())

    def ticker_price(self, symbol, proy):
        url = f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}'
        resp = requests.get(url)
        outcoming = Binance.pretty_data(resp.json())
        return outcoming if outcoming else 'wrong symbol'

# AUTH requests---------------------------------------------------------------------------------------------------------

    def orders_list(self, cid, market):
        # call binance python module or rewrite by myself
        url = 'https://api.binance.com/api/v3/openOrders'
        # создание query string для использования в hash_creator, тк кодировать надо только параметры, но не url
        payload = {
            'timestamp': int(time.time()*1000),
            #'recWindow': 5000,  # можно не указывать, дефолтное значение такое же
            'symbol': market
                   }
        # биржа просит передавать апи ключ в заголовке
        headers = {
            'X-MBX-APIKEY': Binance.data_encrypter()['api_key']
                   }
        payload['signature'] = AllExchange.hash_creator(Binance.data_encrypter()['secret'], payload, '256')
        resp = requests.get(url, params=payload, headers=headers)
        return resp.text

    def create_order(self, cid):
        url = 'https://api.binance.com/api/v3/order/test'
        payload = {}


# ==============================Bittrex=================================================================================


class Bittrex(AllExchange):
    @staticmethod
    def pretty_data(data):
        ticker_name = []
        # tickers name
        try:
            for tickers in data['result']:
                ticker_name.append([tickers['MarketName'], tickers['BaseCurrencyLong'], tickers['MarketCurrencyLong']])
        # wrong symbol and ticker price
        except TypeError:
            return None if (not data['result']) else data['result'].get('Last')
        return [i[0] for i in ticker_name]

    def all_ticker_name(self, proxy):
        url = 'https://api.bittrex.com/api/v1.1/public/getmarkets'
        resp = requests.get(url, proxies=proxy)
        return Bittrex.pretty_data(resp.json())

    def ticker_price(self, symbol, proxy):
        url = f'https://api.bittrex.com/api/v1.1/public/getticker?market={symbol}'
        resp = requests.get(url, proxies=proxy)
        outcoming = Bittrex.pretty_data(resp.json())
        return outcoming if outcoming else 'wrong symbol'

# AUTH requests---------------------------------------------------------------------------------------------------------

    # market - ticker symbol that you want
    def orders_list(self, cid, market):
        url = 'https://api.bittrex.com/api/v1.1/market/getopenorders?'
        secret = b'nottrue'  # select
        api_key = b'nottrue'
        payload = {
            'apikey': api_key,  # select или что-то еще, но надо достать
            'nonce': int(time.time()*1000),
            'market': market
            }
        sign = AllExchange.hash_creator(secret, payload, '512', url)
        headers = {
            'apisign': sign
            }
        resp = requests.get(url, params=payload, headers=headers)
        return resp.json()

    def create_order(self, cid):
        pass


# ==============================BITFINEX================================================================================


class Bitfinex(AllExchange):
    @staticmethod
    def pretty_data(data):
        ticker_name = []
        # ticker price
        if len(data) == 1:
            return data[0][-4]
        # tickers name
        elif len(data) > 1:
            for tickers in data:
                ticker_name.append(tickers[0])
        # wrong symbol
        else:
            pass
        return ticker_name

    def all_ticker_name(self, proxy):
        url = 'https://api-pub.bitfinex.com/v2/tickers?symbols=ALL'
        resp = requests.get(url, proxies=proxy)
        return Bitfinex.pretty_data(resp.json())

    def ticker_price(self, symbol, proxy):
        url = f'https://api-pub.bitfinex.com/v2/tickers?symbols={symbol}'
        resp = requests.get(url, proxies=proxy)
        outcoming = Bitfinex.pretty_data(resp.json())
        return outcoming if outcoming else 'wrong symbol'

# AUTH requests---------------------------------------------------------------------------------------------------------

    def orders_list(self, cid, symbol):
        pass

    def create_order(self, cid):
        pass



#bot = Bittrex()
#bot.all_ticker_name({'https': 'https://eefuosho:0WnTysAp@{}:51689/'.format('78.153.149.57')})
#print(time.time()-a)
