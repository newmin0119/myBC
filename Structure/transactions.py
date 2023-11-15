import time
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from Crypto_tools import *
from random import random,randrange

def make_transaction(input_pubkey,output_pubKey,Vid=None,modelName="",tradeCnt=1,price=0,manufacturedTime=''):
    """
    transaction 구조
    {
        'Vid': 'hexdigest',
        'trandeCnt': int,
        'modelName': 'hexdigest, str',
        'manufacturedTime': 'date, str (____.__.__)',
        'price': int,
        'tradingTime': 'date, str (____.__.__)',
        'input': 'hexdigest,str',
        'output': 'hexdigest, str',
        'txid': 'hexdigest, str',
        'sig': 'hexdigest, str'
    }
    """
    a = {}
    if(Vid==None):
        a['Vid'] = sha256(str(random()).encode()).hexdigest()
    else:
        a['Vid'] = Vid
    a['trandeCnt'] = tradeCnt
    a['modelName'] = modelName
    a['manufacturedTime'] = manufacturedTime
    a['price']=price
    a['tradingTime']=time.strftime('%Y.%m.%d', time.localtime(time.time()))
    
    a['input'] = input_pubkey.to_string()
    a['output'] = output_pubKey.to_string()
    a['txid'] = sha256(str(a).encode()).hexdigest()

    return a

### 예시 transaction
def print_example():
    print(make_transaction('seller pubkey','buyer pubkey',modelName='Genesis',price=30000000,manufactured='2023.10.31'))

### 예시 transaction 출력 end ###