from .Blocks import *
from .transactions import *
Target_N = '0000010000000000000000000000000000000000000000000000000000000000'
is_not_include = -2
is_in_longest = -1
latest = -1
block_info = 0
header_hash = 1
class BlockChain:
    """
    {
        Longest_Chain: list()
            : 현재 클래스가 판단하는 LongestChain을 리스트 형태로 저장
        orphan_chains: list()
            : 현재 LongestChain으로 판단되지 않은 fork를 통해 생성된 모든 orphan chain을 각각 Blockchain에 담아 리스트 형태로 저장
    }
    A Class of Block.
    It's module and object
    It has 3 functions
        - find_block
            : 인자로 Block의 hash값과 height를 받음
            : 두 개의 정보로 Block이 현재 Class의 어느 체인에 위치하는 지를 탐색, 결과를 반환
                -> Longestchain에 있다면 결과는 -1
                -> Orphan chain에 있다면 결과는 self.orphan_chains 상의 인덱스
                -> 그 어디에도 없다면 -2
        - add_block
            : 인자로 Block의 데이터를 넘겨 받음
            : 이후 가장 먼저 Block이 이미 체인에 등록되어있는지 판단
                -> 이미 있다면 False를 반환 아니라면 계속 진행
            : 없다면 prevBlock을 을 find_block, 결과에 따라 아래를 진행
                -> 1인 경우 longest chain에
                    - height가 longest chain height + 1인 경우 이어 붙이고
                    - 아닌 경우 orphan에 새로운 chain 추가
                -> 0 이상인 경우
                    - i 번째 orphan에 추가
                    - 이떼, height가 longest chain height + 1인 경우 
                        longest에 맞는 지점부터 이어 붙이고
                        기존 longest에서 떼어진 부분과 orphan chain의 orphan을 orphan_chains로 이동
        - mining
            : Fullnode Process에서 mining을 구현하기 전까지 쓰던 함수
            : Test 진행 시, 빠르게 단일 채굴로 CPU 공유 없이 Chain의 길이를 늘리고자 사용하였음
    """
    def __init__(self, genesis_block,start_height,is_orphan=False) -> None:
        self.start_height = start_height
        self.Longest_Chain = []
        if is_orphan:
            for block,hash in genesis_block:
                self.Longest_Chain.append((block,hash))
        else:
            self.Longest_Chain.append((genesis_block,sha256(str(genesis_block.Header).encode()).hexdigest()))
        self.orphan_chains = []
    
    def __str__(self) -> str:
        ret = ''
        for block,_ in reversed(self.Longest_Chain):
            ret += '\n\033[34m----------------------------------------------------------------------------------------------------\033[0m\n'
            ret += block.__str__()
            ret += '\n\033[34m----------------------------------------------------------------------------------------------------\n\033[0m'
        return ret


    def find_block(self,hash,height):
        '''
        BlockChain에서 해당하는 헤더의 hash값과 height으로 block의 위치를 알려줌
         - Longest_Chain에 포함된경우 -1,
         - orphan_chains에 포함된 경우 해당하는 orphan_chain의 인덱스를 반환
         - 모두 포함되지 않은 경우 -2를 반환
        '''
        if height<len(self.Longest_Chain):
            for a,b in self.Longest_Chain:
                if b == hash:
                    return is_in_longest
        n = len(self.orphan_chains)
        for i in range(n):
            orphan = self.orphan_chains[i]
            ret = orphan.find_block(hash,height)
            if ret != is_not_include:
                return i
        return is_not_include

    def add_block(self, block):
        '''
        BlockChain에 block을 연결
        i가 -1인 경우 longest chain에
            - height가 longest chain height + 1인 경우 이어 붙이고
            - 아닌 경우 orphan에 새로운 chain 추가
        i가 0 이상인 경우
            - i 번째 orphan에 추가
            이떼, height가 longest chain height + 1인 경우 
                longest에 맞는 지점부터 이어 붙이고
                    기존 longest에서 떼어진 부분과
                    orphan chain의 orphan을
                orphan_chains로 이동
        '''
        hash = sha256(str(block.Header).encode()).hexdigest()
        prevHash = block.Header['prevHash']
        height = block.Header['blockHeight']
        if self.find_block(hash,height) != is_not_include:
            return False
        i = self.find_block(prevHash,height-1)
        if i==is_not_include:
            return False
        if i==is_in_longest:
            if height == len(self.Longest_Chain) + self.start_height:
                self.Longest_Chain.append((block,hash))
            else:
                self.orphan_chains.append(BlockChain(block,height))
        else:
            self.orphan_chains[i].add_block(block)
            if height == len(self.Longest_Chain):
                start_height = self.orphan_chains[i].start_height
                self.orphan_chains.append(BlockChain(self.Longest_Chain[start_height:],start_height,True))
                self.Longest_Chain = self.Longest_Chain[:start_height]+self.orphan_chains[i].Longest_Chain
                self.orphan_chains[i] = self.orphan_chains[i].orphan_chains
        return block
    
    # 아마 이제는 쓰지 않을 함수
    def mining(self,txs):
        """
        Mining process
        """
        header = {
            'blockHeight': self.Longest_Chain[latest][block_info].Header['blockHeight']+1,
            'prevHash': self.Longest_Chain[latest][header_hash],
            'nonce': 0,
            'Merkle_root': ''
        }
        # set_merkle 함수 활용 merkle 생성
        Merkle_tree = Block.set_merkle(txs)
        header['Merkle_root'] = Merkle_tree[1]
        # nonce 값 조정, header's hash<=self.target_N
        while sha256(str(header).encode()).hexdigest()>Target_N:
            header['nonce']+=1
        B = Block(header,Merkle_tree)
        return B


### 예시 BlockChain 출력 ###
def print_example():
    tx = []
    sk = SigningKey.generate()
    pk = sk.get_verifying_key()
    for i in range(15):
        tx.append(str(make_transaction(pk,pk,modelName='Genesis',price=i)))
    header= {
                    'blockHeight':0,
                    'prevHash':'asdfasdfadsfasdfasdfasdfasdf',
                    'nonce': 12345678,
                    'Merkle_root': ''
            }
    B = Block(header,['0']) # genesis

    BC = BlockChain(B,0) # genesis만 존재하는 블록체인 생성
    B = BC.mining(tx[:5])
    print(BC.find_block(sha256(str(B.Header).encode()).hexdigest(),1))
    print(BC.add_block(B))
    print(BC.find_block(sha256(str(B.Header).encode()).hexdigest(),1))
    # header= {
    #                 'blockHeight':2,
    #                 'prevHash':BC.orphan_chains[0].Longest_Chain[0][1],
    #                 'nonce': 12345678,
    #                 'Merkle_root': merkle[1]
    #         }
    # BC.add_block(Block(header,merkle)) # orphan에 존재하는 chain에 추가되는 block 삽입
    # ### 결국 orphan이 longest로 이동 ###
    # print(BC.__str__())
    

# print_example()
### 예시 BlockChain 출력 end ###