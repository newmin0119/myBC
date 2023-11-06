import time
from hashlib import sha256
from random import random,randrange

def HASH256(x):
    return sha256(sha256(x.encode()).hexdigest().encode()).hexdigest()

def make_transaction(input_pubkey,output_pubKey,Vid=None,modelName="",tradeCnt=1,price=0):
    a = {}
    if(Vid==None):
        a['Vid'] = sha256(str(random()).encode()).hexdigest()
    else:
        a['Vid'] = Vid
    a['trandeCnt'] = tradeCnt
    a['modelName'] = modelName
    a['manufacturedTime'] = str(randrange(1990,2024))+'.'+str(randrange(1,13))+'.'+str(randrange(1,28))
    a['price']=price
    a['tradingTime']=time.strftime('%Y.%m.%d', time.localtime(time.time()))
    
    a['input'] = input_pubkey
    a['output'] = output_pubKey
    a['txid'] = sha256(str(a).encode()).hexdigest()

    a['sig'] = '' ### crypto.load_certificate() ### load_certificate() 서명 부분 더 정확히 수정 필요

    return a

### 예시 transaction
print(make_transaction('seller pubkey','buyer pubkey',modelName='Genesis',price=30000000))
### 예시 transaction 출력 end ###