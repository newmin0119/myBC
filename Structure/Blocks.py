import sys, os,time
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
    A Class of Block.
    It's module and object
    It contains 3 static functions
        - set_merkle
            : 전달받은 트랜잭션 리스트를 통해 머클트리를 구성
            : 인덱스 1부터 시작하는 리스트 형태
            : 각 인덱스 i 에 대해
                -> i//2는 parent
                -> 따라서 i*2 와 i*2+1은 children
            : 이진트리를 구성하고, 리프노드가 모두 같은 depth에 위치하기 위해 마지막 트랜잭션의 hash값을 복사하여 삽입
            : 또한 리프노드가 더미 데이터가 아닌 경우 인덱스 i에 대해 i*2의 인덱스에 트랜잭션 데이터를 저장
            : 따라서 트랜잭션의 개수 <= N인 2의 제곱수 N에 대해 N*4가 총 트리의 노드 수 크기
            : 또한 리프노드까지의 depth는 log2 N
        - find_txs
            : 전달받은 머클트리에서 트랜잭션을 뽑아냄
            : 위에서 설명한 set_merkle의 노드 삽입 순서의 역순으로 진행
            : 각 리프노드를 찾고, 처음 더미데이터를 발견할때까지가 트랜잭션의 hash값
            : 그렇게 찾은 index*2에 위치한 실제 트랜잭션 데이터를 list에 담아 반환
        - rebuild_from_str
            : string 형태로 변환된 block에서 헤더와 머클트리를 재구성하는 함수
            : 다만, 구현된 Process에서 실제 사용하지는 함수
            : 후에 로컬환경이 아닌 실제 네트워크 상에서 운용된다면, socket을 통해 데이터를 전달할 때 사용 가능
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
        ret += '\033[32mHeader: \n'
        for val in self.Header:
            ret+= '\t\033[32m' + val + ': \033[0m' + str(self.Header[val]) + '\n'
        ret += '\033[32mtransactions: \n------------------------------'
        
        txs = self.find_txs(self.Merkle)
        for i in range(len(txs)):
            ret += '\n\t\033[32m'+str(i)+ ': \033[0m' + str(eval(txs[i])['Vid']) + ', \033[32m거래 순서: \033[0m' + str(eval(txs[i])['tradeCnt'])
        return ret

    ### Merkle tree 구성 함수
    @staticmethod
    def set_merkle(txs) -> list:
        '''
        transaction을 트리의 리프노드에 저장, 이진 트리 형태 유지를 위해 리프노드 depth의 마지막 여분은 가장 마지막 트랜잭션의 해쉬값 복사본
        또한, 리프노드의 보조 트리가 하나 더 존재, 리프노드의 2배수 index의 트리 노드는 각 트랜잭션이 존재
        또한 이진 트리의 index 삽입과 연산의 효율성을 위해, list에 저장한 트리의 루트 노드의 index는 1
        따라서, index 0은 None
        '''
        txs = list(txs)
        N = len(txs)
        leaf_n = 1
        while leaf_n<N: leaf_n<<=1
        merkle_tree = [None]*(leaf_n<<2)
        last_leaf = ''
        for i in range(leaf_n):
            if i<N:
                ### merkle_tree leaf node인 경우 트랜잭션의 id를 sha256 hash를 두 번 거친 값
                merkle_tree[i+leaf_n]=HASH256(eval(txs[i])['txid'])
                last_leaf = merkle_tree[i+leaf_n]
                ### leaf node 및 2의 제곱수 형태 형성을 위한 더미데이터 아닌 경우 트랜잭션 정보 삽입
                merkle_tree[(i+leaf_n)<<1]=txs[i] 
            else:
                ### 2의 제곱수 형태 형성을 위한 더미데이터 삽입
                merkle_tree[i+leaf_n]=last_leaf
        while leaf_n>1:
            leaf_n>>=1
            for i in range(leaf_n):
                ### 리프 노드가 아닌 노드는 자식노드의 값을 concatnate 한 값을 sha256 hash를 두 번 거친 값
                merkle_tree[i+leaf_n]=HASH256(merkle_tree[(i+leaf_n)<<1]+merkle_tree[((i+leaf_n)<<1)+1])
        if merkle_tree[1]=='':
            merkle_tree[1]=HASH256('DUMMY')
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
            if merkle[i] and merkle[i]!='0':
                txs.append(merkle[i])
        return txs
    @staticmethod
    def rebuild_from_str(str_Block):
        list_Block_component = list(str_Block.split('\n'))
        Header = {}
        Header['blockHeight']    = int(list_Block_component[1].split()[1])
        Header['prevHash']      = list_Block_component[2].split()[1]
        Header['nonce']         = int(list_Block_component[3].split()[1])
        Header['Merkle_root']   = list_Block_component[4].split()[1]
        transactions            = []
        for transaction in list_Block_component[8:]:
            if transaction=='------------------------------': continue
            transactions.append(transaction[3:])
        Merkle = Block.set_merkle(transactions)
        return Block(Header,Merkle)


### 예시 Block ###
def print_example():
    tx = []
    sk = SigningKey.generate()
    vk = sk.get_verifying_key()
    for i in range(5):
        tx.append(str(make_transaction(vk,vk,modelName='Genesis',price=i)))
    merkle = Block.set_merkle(tx)
    header= {
                    'blockHeight':0,
                    'prevHash':'asdfasdfadsfasdfasdfasdfasdf',
                    'nonce': 12345678,
                    'Merkle_root': merkle[1]
            }
    B = Block(header,merkle)
    print(B.__str__())
    '''
    txs = B.find_txs(B.Merkle)
    for transaction in txs:
        print(transaction)
    '''
# print_example()
### 예시 Block 출력 end ###