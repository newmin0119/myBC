import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import socket
from multiprocessing import Manager

from child_process import FullNode_Process, UserNode_Process
from Blockchain.Block import Block
   
if __name__=='__main__':
    manager = Manager()
    N,M = map(int,input().split())
    genesis = Block({
        'blockHeight':0,
        'prevHash':'',
        'nonce':0,
        'Merkle_tree':['0']
    })
    fullnodes = [FullNode_Process('192.0.0.'+'%d'%i,8000,genesis,10000000) for i in range(N)]
    for node in fullnodes:
        node.start()
    for node in fullnodes:
        node.join()