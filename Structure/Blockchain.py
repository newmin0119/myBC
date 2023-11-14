from .Blocks import *
from .transactions import *
Target_N = '0000080000000000000000000000000000000000000000000000000000000000'
is_not_include = -2
is_in_longest = -1
latest = -1
block_info = 0
header_hash = 1
class BlockChain:
    
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
            ret += '\n----------------------------------------------------------------------------------------------------\n'
            ret += block.__str__()
            ret += '\n----------------------------------------------------------------------------------------------------\n'
        return ret


    def find_prev_block(self,hash,height):
        '''
        BlockChain에서 해당하는 헤더의 hash값과 height으로 block의 위치를 알려줌
         - Longest_Chain에 포함된경우 -1,
         - orphan_chains에 포함된 경우 해당하는 orphan_chain의 인덱스를 반환
         - 모두 포함되지 않은 경우 -2를 반환
        '''
        if self.Longest_Chain[height-self.start_height][header_hash] == hash:
            return is_in_longest
        n = len(self.orphan_chains)
        for i in range(n):
            orphan = self.orphan_chains[i]
            ret = orphan.find_prev_block(hash,height)
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
        prevHash = block.Header['prevHash']
        height = block.Header['blockHeight']
        i = self.find_prev_block(prevHash,height-1)
        hash = sha256(str(block.Header).encode()).hexdigest()
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
        self.add_block(B)
        return B


### 예시 BlockChain 출력 ###
def print_example():
    tx = []
    for i in range(15):
        tx.append(make_transaction('seller pubkey','buyer pubkey',modelName='Genesis',price=i))
    merkle = Block.set_merkle(tx[:5])
    header= {
                    'blockHeight':0,
                    'prevHash':'asdfasdfadsfasdfasdfasdfasdf',
                    'nonce': 12345678,
                    'Merkle_root': merkle[1]
            }
    B = Block(header,merkle) # genesis

    BC = BlockChain(B,0) # genesis만 존재하는 블록체인 생성
    merkle = Block.set_merkle(tx[5:10])
    for i in range(2):
        header= {
                        'blockHeight':1,
                        'prevHash':BC.Longest_Chain[0][1],
                        'nonce': i,
                        'Merkle_root': merkle[1]
                }
        BC.add_block(Block(header,merkle)) # 처음은 longest chain에, 두번째는 orphan에 block 삽입됨
    merkle = Block.set_merkle(tx[10:])
    header= {
                    'blockHeight':2,
                    'prevHash':BC.orphan_chains[0].Longest_Chain[0][1],
                    'nonce': 12345678,
                    'Merkle_root': merkle[1]
            }
    BC.add_block(Block(header,merkle)) # orphan에 존재하는 chain에 추가되는 block 삽입
    ### 결국 orphan이 longest로 이동 ###
    print(BC.__str__())
    
        
# print_example()
### 예시 BlockChain 출력 end ###