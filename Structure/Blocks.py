import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from .transactions import *
from Crypto_tools import *
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
    def __init__(self, *args):
        '''
        args[0] : Block의 Header
        args[1] : 포함시킬 transaction
        '''
        self.Header = args[0]
        self.Merkle=args[1]
    
    ### Block의 데이터를 출력하는 함수, 객체의 반환형을 str 형태로, dict 형태로 복원 가능
    def __str__(self) -> str:
        ret = ''
        ret += 'Header: \n'
        for val in self.Header:
            ret+= val+': '+str(self.Header[val])+'\n'
        ret += '\ntransactions: \n------------------------------'
        txs = self.find_txs(self.Merkle)
        for i in range(len(txs)):
            ret += '\n'+str(i)+ ': ' + str(txs[i])+'\n------------------------------'
        return ret

    ### Merkle tree 구성 함수
    @staticmethod
    def set_merkle(tx) -> list:
        '''
        transaction을 트리의 리프노드에 저장, 이진 트리 형태 유지를 위해 리프노드 depth의 마지막 여분은 가장 마지막 트랜잭션의 해쉬값 복사본
        또한, 리프노드의 보조 트리가 하나 더 존재, 리프노드의 2배수 index의 트리 노드는 각 트랜잭션이 존재
        또한 이진 트리의 index 삽입과 연산의 효율성을 위해, list에 저장한 트리의 루트 노드의 index는 1
        따라서, index 0은 None
        '''
        N = len(tx)
        leaf_n = 1
        while leaf_n<N: leaf_n<<=1
        merkle_tree = [None]*(leaf_n<<2)
        last_leaf = ''
        for i in range(leaf_n):
            if i<N:
                ### merkle_tree leaf node인 경우 트랜잭션의 id를 sha256 hash를 두 번 거친 값
                merkle_tree[i+leaf_n]=HASH256(tx[i]['txid'])
                last_leaf = merkle_tree[i+leaf_n]
                ### leaf node 및 2의 제곱수 형태 형성을 위한 더미데이터 아닌 경우 트랜잭션 정보 삽입
                merkle_tree[(i+leaf_n)<<1]=tx[i] 
            else:
                ### 2의 제곱수 형태 형성을 위한 더미데이터 삽입
                merkle_tree[i+leaf_n]=last_leaf
        while leaf_n>1:
            leaf_n>>=1
            for i in range(leaf_n):
                ### 리프 노드가 아닌 노드는 자식노드의 값을 concatnate 한 값을 sha256 hash를 두 번 거친 값
                merkle_tree[i+leaf_n]=HASH256(merkle_tree[(i+leaf_n)<<1]+merkle_tree[((i+leaf_n)<<1)+1])
        return merkle_tree

    @staticmethod
    def find_txs(merkle) -> list:
        '''
        Merkle트리는 인덱스 1 부터 시작하는 이진트리의 형태
        따라서 트리 노드의 총 개수는 마지막 depth의 노드 수의 두배 ( 정확히는 2n+1)
        그러므로 길이의 오른쪽 비트 쉬프트 1은 가장 말단에 존재하는 트랜잭션의 시작 인덱스
        또한 트랜잭션은 자신의 부모 노드의 인덱스의 2배에 저장되어있으므로, index 2차이로 저장
        또한, 더미데이터 혹은 홀수번째의 index에는 None이 저장되어 있음
        따라서 이를 고려해 리스트에 올바른 트랜잭션만 담아 반환
        '''
        finish = len(merkle)
        start = finish>>1
        txs = []
        for i in range(start,finish,2):
            if merkle[i]:
                txs.append(merkle[i])
        return txs


### 예시 Block ###
def print_example():
    tx = []

    for i in range(5):
        tx.append(make_transaction('seller pubkey','buyer pubkey',modelName='Genesis',price=i))
    merkle = Block.set_merkle(tx)
    header= {
                    'blockHeight':0,
                    'prevHash':'asdfasdfadsfasdfasdfasdfasdf',
                    'nonce': 12345678,
                    'Merkle_root': merkle[1]
            }
    B = Block(header,merkle)
    txs = B.find_txs(B.Merkle)
    for transaction in txs:
        print(transaction)
# print_example()
### 예시 Block 출력 end ###