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
    a['tradeCnt'] = tradeCnt
    a['modelName'] = modelName
    a['manufacturedTime'] = manufacturedTime
    a['price']=price
    a['tradingTime']=time.strftime('%Y.%m.%d', time.localtime(time.time()))
    
    a['input'] = input_pubkey.to_string()
    a['output'] = output_pubKey.to_string()
    a['txid'] = sha256(str(a).encode()).hexdigest()

    return a

def validate_transaction(prev_tx,target_tx) -> str:
        if prev_tx is not None:
            ## 1) txs(k)'s buyer == txs(k-1)'s seller
            if prev_tx['output']!=target_tx['input']:
                return 'This transaction\'s input is not prev_Transaction\'s output'
            ## 2) Check immutable value
            if prev_tx['Vid']!=target_tx['Vid']:
                return 'Vid is not prev_Transaction\'s'
            if prev_tx['modelName']!=target_tx['modelName']:
                return 'ModelName is not prev_Transaction\'s'
            if prev_tx['manufacturedTime']!=target_tx['manufacturedTime']:
                return 'ManufacturedTime is not prev_Transaction\'s'
        
        ## 3) Verify signature
        if not verify_sig(target_tx['sig'],VerifyingKey.from_string(target_tx['input']),target_tx['txid']):
            return 'Signature is not valid'
        return 'Verified Successfully'
### 예시 transaction
def print_example():
    print(make_transaction('seller pubkey','buyer pubkey',modelName='Genesis',price=30000000,manufactured='2023.10.31'))

### 예시 transaction 출력 end ###