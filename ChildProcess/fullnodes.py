import sys, os
from socket import *
from multiprocessing import Queue
from threading import Thread,Lock,Event
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from Crypto_tools import *
from Structure.Blocks import *
from Structure.Blockchain import *
from Structure.transactions import validate_transaction
Target_N = '0000008000000000000000000000000000000000000000000000000000000000'
'''
본 클래스는 FullNode가 Process 클래스를 상속받지 않고,
target으로 지정해서 Multiprocessing 되도록 설계한 클래스이다.
'''
class FullNode():
    """
    A class of FullNode, generated by MasterProcess

    """
    # 클래스 최초 생성 함수
    def __init__(self,*args) -> None:
        # args
        # genesisBlock,r_pipe,peer_list,w_pipe,fullnode_i
        self.Blockchain             =   BlockChain(args[0],0)
        self.memset                 =   set()
        self.read_pipe              =   args[1]
        self.peer_pipes             =   args[2]
        self.write_pipe             =   args[3]
        self.node_number            =   args[4]
        self.event_for_Snapshot     =   args[5]
        self.user_transactions  =   dict()
    
    def run(self):
        self.blockchain_lock            =   Lock()
        self.block_recv_event           =   Event()
        self.mining_thread              =   Thread(target=self.mining_process)
        self.snapshot_thread            =   Thread(target=self.check_snapshot)
        self.listen_block_threads       =   []
        self.block_q                    =   Queue()
        for r_pipe,w_pipe in self.peer_pipes:
            self.listen_block_threads.append(Thread(target=self.listening_block,args=(r_pipe,self.block_q,)))
        self.gather_block_thread        = Thread(target=self.listen_block,args=(self.block_q,))
        self.listen_transaction_thread = Thread(target=self.listen_transaction)

        self.listen_transaction_thread.start()
        self.mining_thread.start()
        for block_listen_thread in self.listen_block_threads:
            block_listen_thread.start()
        self.gather_block_thread.start()
        self.snapshot_thread.start()

        self.listen_transaction_thread.join()
        self.mining_thread.join()
        for block_listen_thread in self.listen_block_threads:
            block_listen_thread.join()
        self.gather_block_thread.join()
        self.snapshot_thread.join()

    def check_snapshot(self):
        while True:
            self.event_for_Snapshot.wait()
            print('#########F',self.node_number,'\'s Longest Chain Snapshot##########',sep='')
            print(self.Blockchain.__str__())
            self.event_for_Snapshot.clear()
    

    # 트랜잭션 인증 함수
    def validate_transaction(self,user_id,i,tx) -> bool:
        prev_tx = self.user_transactions[user_id][tx['tradeCnt']-1][i]
        return validate_transaction(prev_tx,tx)

    #def


    # 채굴 함수
    def mining_process(self):
        """
        Mining process
        """
        while True:
            
            txs = set()
            for _ in range(min(4,len(self.memset))):
                txs.add(self.memset.pop())
            self.memset.update(txs)         # mining 중간에 해당 프로세스가 중단되는 것을 고려하여, 아직 memset에서 pop 하지 않음
            # 적절히 txs 안에 memset에서 골라오는 함수 필요
            
            header = {
                'blockHeight': self.Blockchain.Longest_Chain[latest][block_info].Header['blockHeight']+1,
                'prevHash': self.Blockchain.Longest_Chain[latest][header_hash],
                'nonce': 0,
                'Merkle_root': ''
            }
            # set_merkle 함수 활용 merkle 생성
            Merkle_tree = Block.set_merkle(txs)
            header['Merkle_root'] = Merkle_tree[1]
            
            # 다른 node에서 mine 성공 여부 event로 checking
            flag_event_occur    = False
            # nonce 값 조정, header's hash<=self.target_N
            self.block_recv_event.clear()
            while sha256(str(header).encode()).hexdigest()>Target_N:
                if self.block_recv_event.is_set():
                    #print(self.node_number,'가 signal을 받아 종료된다면 이게 출력')
                    flag_event_occur = True
                    break
                header['nonce']+=1
            
            if flag_event_occur:
                #print(self.node_number, '가 signal을 받아 종료되고, 뒷처리를 한다면 이게 출력')
                self.block_recv_event.clear()
                continue

            #print(self.node_number,'가 ',header['blockHeight'],'번째 Block 채굴 성공한 시점')
            mined_Block = Block(header,Merkle_tree)
            
            #print(self.node_number,'의 mining 에서 lock acquire한 시점')
            self.blockchain_lock.acquire()
            self.Blockchain.add_block(mined_Block)
            self.blockchain_lock.release()
            #print(self.node_number,'의 mining 에서 lock Release 한 시점')

            self.memset = self.memset - txs         # mining 중간에 프로세스 종료되지 않고 잘 전달되었다면, memset에서 사용한 트랜잭션 pop
            # 채굴한 block socket으로 peer FullNode로 flooding 하는 함수
            # 먼저 Master Process로 송신
            self.write_pipe.send((self.node_number,mined_Block))
            # 이후 각 peer에게 송신
            self.send_block(mined_Block)

        

    # 채굴된 블락 받는 함수
    # from another FullNode
    def listening_block(self, pipe, q):
        while True:
            q.put(pipe.recv())
    
    # 수신한 블락을 블록체인에 포함하고, 이미 포함했다면 미송신
    def listen_block(self,q):
        while len(self.Blockchain.Longest_Chain)<20:
            recv_block = q.get()
            hash = sha256(str(recv_block.Header).encode()).hexdigest()

            self.block_recv_event.set()
            self.blockchain_lock.acquire()
            is_not_in = self.Blockchain.find_block(hash,recv_block.Header['blockHeight'])
            if not is_not_in:
                continue
            #('listen한 block Blockchain에 포함시도 전에 현재 최말단 block 출력 in',self.node_number)
            #print(self.Blockchain.Longest_Chain[-1][0].Header)
            result=self.Blockchain.add_block(recv_block)
            self.blockchain_lock.release()
            #print(self.node_number,'에 ',recv_block.Header['blockHeight'],'번째 블락 탑색이 끝났다면 출력')
            #print(result)
            if not result:
                continue
            #print(self.node_number,'에 ',recv_block.Header['blockHeight'],'번째 블락이 정상적으로 추가되었다면 출력')
            self.send_block(recv_block)
            
    # 채굴한 블락 flooding 함수
    def send_block(self,block):
        # 이후 각 peer에게 송신
        #print('peer로 송신, ',block.Header['blockHeight'])
        for r_pipe,w_pipe in self.peer_pipes:
            
            w_pipe.send(block)
    
    # 트랜잭션 받는 함수
    # from UserNode
    def listen_transaction(self):
        flag = True
        
        while flag:
            for pipe in self.read_pipe:
                data,user_id = pipe.recv()
                if data==-1:
                    pipe.close()
                    flag = False
                    continue
                if user_id not in self.user_transactions.keys():
                    self.user_transactions[user_id] = []
                self.user_transactions[user_id].append([None]*len(data))
                for i in range(len(data)):
                    if self.validate_transaction(user_id,i,data[i]) == 'Verified Successfully':
                        self.user_transactions[user_id][-1][i]=data[i]
                        self.memset.add(str(data[i]))

    def __str__(self):
        myself = '######################################################################'
        myself += str(self.node_number) + '\'s longest_chain:'
        myself += self.Blockchain.__str__()
        myself += '######################################################################'
        return myself