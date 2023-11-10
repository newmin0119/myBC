import socket,sys,os,time
from random import randint
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from multiprocessing import Process

from FullNode.fullnode import FullNode
from UserNode.usernode import UserNode

class FullNode_Process(Process,FullNode):
    def __init__(self,genesis,target,read_pipe,write_pipe):
        super().__init__()
        FullNode.__init__(self,genesisBlock=genesis,target_N=target)
        self.r_pipe = read_pipe
        self.w_pipe = write_pipe
    
    def run(self):
        print('Full Process 시작')
        if self.r_pipe is not None: 
            data = self.r_pipe.recv()
            for x in data:
                if self.validate_transaction(x):
                    self.tx_pool.append(x)
        print('\n\n채굴 시작\n\n')
        self.mining_process()
        print('채굴종료\n\n')
        # print('채굴종료\n\n직전 채굴된 Block\n\n')
        # print('Header:', self.longest_chain[-1].Header)
        # print('Transactions:', self.longest_chain[-1].transactions)
        self.w_pipe.send(self.longest_chain[-1])
    
        

class UserNode_Process(Process,UserNode):
    def __init__(self, write_pipe):
        super().__init__()
        UserNode.__init__(self,randint(1,3))
        self.pipe = write_pipe
 
    def run(self):
        while(True):
            txs = self.generate_transaction('')
            self.pipe.send(txs)
            time.sleep(15)