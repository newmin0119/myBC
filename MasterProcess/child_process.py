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
        print(self.longest_chain[0])
        pass


class UserNode_Process(Process,UserNode):
    def __init__(self, ip, port):
        super().__init__()
        self.ip = ip
        self.port = port
 