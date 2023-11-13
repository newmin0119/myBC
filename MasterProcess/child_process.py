import sys,os,time
from random import randint
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from multiprocessing import Process

from FullNode.fullnode import FullNode
from UserNode.usernode import UserNode

'''
Sample Transactions
'''
Pubkey  = []

class FullNode_Process(Process,FullNode):
    def __init__(self,*args):
        super().__init__()
        FullNode.__init__(self,args)
    
    def run(self):
        '''
        스레드로 리슨 블락 리슨 트랜잭션 채굴프로세스 돌리기
        '''
        self.mining_process()
        
        # print('채굴종료\n\n직전 채굴된 Block\n\n')
        # print('Header:', self.longest_chain[-1].Header)
        # print('Transactions:', self.longest_chain[-1].transactions)
        self.w_pipe.send(self.longest_chain[-1])
    
        

class UserNode_Process(Process,UserNode):
    def __init__(self, write_pipe):
        super().__init__()
        UserNode.__init__(self,randint(1,3))
        Pubkey.append(self.pk)
        self.pipe = write_pipe
 
    def run(self):
        for output in Pubkey:
            if self.pk == output:
                continue
            txs = self.generate_transaction(output)
            self.pipe.send(txs)
            time.sleep(15)