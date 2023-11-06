from transaction import make_transaction
from Crpto_tools import *
class Block:
    """
    {
        'Header': 
        {
            'blockHeight': int,
            'prevHash': 'hexdigest, str',
            'nonce': 'hexdigest, str',
            'Merkle_root': 'hexdigest, str'
        }
        'transactions':
        [   
            // 순서대로 트리의 index.
            { ... },
            { ... },
            ...
        ]
    }
    """
    ### Block 생성 및 Header 구성
    def __init__(self, args):
        self.blockHeight=args['blockHeight']
        self.prevHash   =args['prevHash']
        self.nonce      =args['nonce']
        self.Merkle_root=args['Merkle_tree'][0]
        self.transactions=args['Merkle_tree']
    
    ### Block의 데이터를 출력하는 함수, 객체의 반환형을 str 형태로, dict 형태로 복원 가능
    def __str__(self) -> str:
        return str({
            'Header':{
                'blockHeight':self.blockHeight,
                'prevHash':self.prevHash,
                'nonce':self.nonce,
                'Merkle_root':self.Merkle_root
            },
            'transactions':self.transactions
        })
    
### Merkle tree 구성 함수
def set_merkle(tx) -> list:
    N = len(tx)
    leaf_n = 1
    while leaf_n<N: leaf_n<<=1
    merkle_tree = ['0']*(leaf_n<<2)
    for i in range(leaf_n):
        if i<N:
            ### merkle_tree leaf node인 경우 트랜잭션의 id를 sha256 hash를 두 번 거친 값
            merkle_tree[i+leaf_n]=HASH256(tx[i]['txid'])
            
            ### leaf node 및 2의 제곱수 형태 형성을 위한 더미데이터 아닌 경우 트랜잭션 정보 삽입
            merkle_tree[(i+leaf_n)<<1]=tx[i] 
        else:
            ### 2의 제곱수 형태 형성을 위한 더미데이터 삽입
            merkle_tree[i+leaf_n]=HASH256(tx[N-1]['txid'])
    while leaf_n>1:
        leaf_n>>=1
        for i in range(leaf_n):
            ### 리프 노드가 아닌 노드는 자식노드의 값을 concatnate 한 값을 sha256 hash를 두 번 거친 값
            merkle_tree[i+leaf_n]=HASH256(merkle_tree[(i+leaf_n)<<1]+merkle_tree[((i+leaf_n)<<1)+1])
    return merkle_tree


### 예시 Block ###
def print_example():
    tx = []
    for i in range(5):
        tx.append(make_transaction('seller pubkey','buyer pubkey',modelName='Genesis',price=i))

    block_arg = {
        'blockHeight':0,
        'prevHash':'asdfasdfadsfasdfasdfasdfasdf',
        'nonce': 12345678,
        'Merkle_tree': set_merkle(tx)[1:]
    }
    print(Block(block_arg))
print_example()
### 예시 Block 출력 end ###