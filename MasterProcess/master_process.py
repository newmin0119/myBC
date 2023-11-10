import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from random import randint
# import socket
from multiprocessing import Manager,Pipe

from child_process import FullNode_Process, UserNode_Process
from Blockchain.Blocks import Block
   

Target_N = '0000080000000000000000000000000000000000000000000000000000000000'

def construct_P2P(N,M,fullnodes,usernodes,listen_Block):
    link_User_to_Full = []
    check = []
    for u_node in range(M):
        f_node = randint(0,N-1)
        while f_node in check:
            f_node = randint(0,N-1)
        readP, writeP = Pipe()
        link_User_to_Full.append((u_node,f_node,writeP,readP))
        check.append(f_node)
    
    link_Master_toFull = []
    
    for _ in range(N):
        read_M, write_F = Pipe()
        link_Master_toFull.append(write_F)
        listen_Block.append(read_M)
    for u,f,w,r in link_User_to_Full:
        usernodes[u] = UserNode_Process(write_pipe=w)
        fullnodes[f] = FullNode_Process(genesis=genesis,target=Target_N,read_pipe=r,write_pipe=link_Master_toFull[f])
    
    for f in range(N):
        if f not in check:
            fullnodes[f] = FullNode_Process(genesis=genesis,target=Target_N,read_pipe=None,write_pipe=link_Master_toFull[f])

if __name__=='__main__':
    manager = Manager()
    
    genesis = Block({
        'blockHeight':0,
        'prevHash':'',
        'nonce':0,
        'Merkle_tree':['0']
    })
    longest = [genesis]

    print('Genests: \n',genesis,end='\n\n')
    N,M = map(int,input().split())
    fullnodes = [None]*N
    usernodes = [None]*M
    listen_Block = []

    construct_P2P(N,M,fullnodes,usernodes,listen_Block)

    while True:
        for node in fullnodes:
            node.start()
        for node in usernodes:
            node.start()
        for read_M in listen_Block:
            B = read_M.recv()
            if B.Header['blockHeight'] > longest[-1].Header['blockHeight']:
                longest.append(B)
                for node in fullnodes:
                    node.kill()
                break
        print(longest[-1].Header['blockHeight'],'번째 Block: \n',longest[-1],end='\n\n')
       