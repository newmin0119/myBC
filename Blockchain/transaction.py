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

class Block:
    def __init__(self, args,transactions):
        self.blockHeight=args['blockHeight']
        self.prevHash   =args['prevHash']
        self.nonce      =args['nonce']
        self.Merkle_tree=self.__set_merkle(transactions)
        self.Merkle_root=self.Merkle_tree[0]
    
    def __set_merkle(self,tx):
        N = len(tx)
        leaf_n = 1
        while leaf_n<N: leaf_n<<=1
        merkle_tree = ['0']*(leaf_n<<2)
        for i in range(leaf_n):
            if i<N:
                merkle_tree[i+leaf_n]=HASH256(tx[i]['txid'])
                merkle_tree[(i+leaf_n)<<1]=tx[i]
            else:
                merkle_tree[i+leaf_n]=HASH256(tx[N-1]['txid'])
        while leaf_n>1:
            leaf_n>>=1
            for i in range(leaf_n):
                merkle_tree[i+leaf_n]=HASH256(merkle_tree[(i+leaf_n)<<1]+merkle_tree[((i+leaf_n)<<1)+1])
        return merkle_tree
    
    def __str__(self) -> str:
        return str({
            'Header':{
                'blockHeight':self.blockHeight,
                'prevHash':self.prevHash,
                'nonce':self.nonce,
                'Merkle-root':self.Merkle_root
            },
            'transactions':self.Merkle_tree
        })

### 예시 Block
tx = []
for i in range(5):
    tx.append(make_transaction('seller pubkey','buyer pubkey',modelName='Genesis',price=i))
block_arg = {
    'blockHeight':0,
    'prevHash':'asdfasdfadsfasdfasdfasdfasdf',
    'nonce':'fdsafdsafdsafdsa',
}
print(Block(block_arg,transactions=tx))
