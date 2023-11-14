import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from random import randint
# import socket
from multiprocessing import Manager,Pipe,Queue,Process

# from child_process import FullNode_Process, UserNode_Process
from ChildProcess.fullnode import FullNode
from ChildProcess.usernode import UserNode
from Structure.Blocks import Block
   

Target_N = '0000080000000000000000000000000000000000000000000000000000000000'
usernodes = []
fullnodes = []
Master_from_full = []
def construct_P2P(N,M,genesis):
    '''
    가상 P2P Network를 구성하는 function
    매개변수 N과 M은 각각 fullnode의 수와 usernode의 수로 대응

    PRNG를 이용하여
     - 각 UserNode는 임의의 FullNode로         Pipe를 이용, 단방향 연결:    user_to_full, full_from_user
     - 각 FullNode는 임의의 다른 FullNode로     Socket을 이용, 양방향 연결:  full_to_full   
     - 그리고 모든 FullNode는 MasterProcess로   Pipe를 이용, 단방향 연결:   full_to_master, mastter_from_full

    이후, 생성된 Pipe와 Socket을 각각 User와 Full Node class로 argument로 전달
    이때, 임의의 ip와 port번호 ( 여기서는 Bitcoin의 port번호 8333을 이용 )를 같이 전달
    '''
    user_to_full = []
    full_from_user = [list() for _ in range(N)]
    full_to_full = [list() for _ in range(N)]
    full_to_Master = []
    
    # User <-> Full 구성
    for user_num in range(M):
        full_num = randint(0,M-1)
        read_pipe,write_pipe = Pipe()
        user_to_full.append(write_pipe)
        full_from_user[full_num].append(read_pipe)

    # Full <-> Full 구성
    # 이중 for문과 randint 0,1을 이용 50%의 확률로 두 노드 사이의 연결이 있는 지 없는 지 결정
    for full_A in range(N-1):
        for full_B in range(full_A+1,N):
            if randint(0,1):
                full_to_full[full_A].append('192.168.0.'+str(full_B))
                full_to_full[full_B].append('192.168.0.'+str(full_A))
    
    for full_num in range(N):
        print(full_num,': ',full_to_full[full_num])

    # Full <-> Master 구성
    for full_num in range(N):
        read_pipe, write_pipe = Pipe()
        full_to_Master.append(write_pipe)
        Master_from_full.append(read_pipe)


    # usernode Process 생성
    for user_num in range(M):
        # user_id, car_num, write_pipe
        usernodes.append(UserNode(user_num,randint(1,3),user_to_full[user_num]))

    # fullnode Process 생성
    for full_num in range(N):
        # genesisBlock,ip,port,r_pipe,peer_list,w_pipe,fullnode_i
        fullnodes.append(FullNode(  genesis,
                                    '192.168.0.'+str(full_num),
                                    8333,
                                    full_from_user[full_num],
                                    full_to_full[full_num],
                                    full_to_Master[full_num],
                                    full_num
                                )
                        )
def listen_Block(pipe,q):
    while True:
        q.put(pipe.recv())

if __name__=='__main__':
    manager = Manager()
    
    # Genesis Block 
    genesis = Block({
        'blockHeight':0,
        'prevHash':'',
        'nonce':0,
        'Merkle_root':['0']
    },['0'])

    # Master Process가 관리하는 longest Chain

    # print('Genests: \n',genesis,end='\n\n')
    
    #FullNode 수와 UserNode 수 입력
    N,M = map(int,input().split())

    """
    P2P Network 구성
    return값이 아닌, 전역변수 Process리스트인 usernodes와  fullnodes에 저장
    """
    construct_P2P(N,M,genesis)
    q = Queue()
    for pipe in Master_from_full:
        p = Process(target=listen_Block,args=(pipe,q,))
        p.start()

    for fullnode in fullnodes:
        fullnode.start()
    
    for usernode in usernodes:
        usernode.start()
    while True:
        if not q.empty():
            Fi, tempblock = q.get()
    
    

    '''
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
    '''
       