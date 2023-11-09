import socket,sys,os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from multiprocessing import Process

from FullNode.fullnode import FullNode
from UserNode.usernode import UserNode

class FullNode_Process(Process,FullNode):
    def __init__(self, ip, port,genesis,target):
        super().__init__()
        FullNode.__init__(self,genesisBlock=genesis,target_N=target)
        self.ip = ip
        self.port = port
    
    def run(self):
        print(self.ip, self.port)
        print('\n\nGenesisBlock\n\n')
        print(self.longest_chain[0].Header)
        print('\n\n채굴 시작\n\n')
        self.mining_process()
        print('채굴종료\n\n직전 채굴된 Block\n\n')
        print(self.longest_chain[-1].Header)
        pass


class UserNode_Process(Process,UserNode):
    def __init__(self, ip, port):
        super().__init__()
        self.ip = ip
        self.port = port
 