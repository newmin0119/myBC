import sys, os,time
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from random import randint
# import socket
from multiprocessing import Manager,Pipe, Queue, Process,Event
from threading import Thread
# from child_process import FullNode_Process, UserNode_Process
from ChildProcess.fullnodes import FullNode
from ChildProcess.usernode import UserNode
from Structure.Blocks import Block
from Structure.Blockchain import BlockChain
from Structure.transactions import validate_transaction

usernodes = []
fullnodes = []
Master_from_full = []
events_for_snapshot = []
Mined_Block_by_FullNode = []
transactions_by_Vid = dict()
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
                print(full_A,'<--->',full_B)
                Aread_pipe, Bwrite_pipe = Pipe()
                Bread_pipe, Awrite_pipe = Pipe()
                full_to_full[full_A].append((Aread_pipe,Awrite_pipe))
                
                full_to_full[full_B].append((Bread_pipe,Bwrite_pipe))
    '''
    fullnode의 링크를 보이는 print
    for full_num in range(N):
        print(full_num,': ',full_to_full[full_num])
    '''
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
        event_for_snapshot  = Event()
        events_for_snapshot.append(event_for_snapshot)
        fullnodes.append(FullNode(  genesis,
                                    full_from_user[full_num],
                                    full_to_full[full_num],
                                    full_to_Master[full_num],
                                    full_num,
                                    event_for_snapshot
                                )
                        )
def listen_Block(pipe,q):
    while True:
        q.put(pipe.recv())

def receive_block(q):
    global Mined_Block_by_FullNode
    while True:
        Fi, tempblock = q.get()
        print('#####F%d mined Succesfully!!!!######\n<<-- Block -->>' % Fi,
              tempblock.Header['blockHeight']
            # tempblock    
            )
        Mined_Block_by_FullNode[Fi].append(tempblock)
        transactions = Block.find_txs(tempblock.Merkle)
        for transaction in transactions:
            if transaction['Vid'] not in transactions_by_Vid.keys():
                transactions_by_Vid[transactions_by_Vid] = []
            transactions_by_Vid[transaction['Vid']].append((transaction,tempblock.Header['blockHeight']))

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
    pipe_list = []
    for pipe in Master_from_full:
        p = Thread(target=listen_Block,args=(pipe,q,))
        p.start()
        pipe_list.append(p)
    
    for usernode in usernodes:
        usernode.start()
    fullnode_process = []
    for fullnode in fullnodes:
        fp = Process(target=fullnode.run)
        fp.start()
        fullnode_process.append(fp)
        Mined_Block_by_FullNode.append(list())
    
    recv_thread = Thread(target=receive_block,args=(q,))
    recv_thread.start()
    while True:
        op = input()
        if op=='exit':
            for fullnode in fullnodes:
                fullnode.kill()
            for usernode in usernodes:
                usernode.kill()
            recv_thread.terminate()
            
        elif op.split()[0]=='snapshot':
            if len(op.split()) !=3:
                print('Not a valid operation. Please input likes \'snapshot myBC ALL or <Fi>\'')
            if op.split()[2]=='ALL':
                for event in events_for_snapshot:
                    event.set()
                    time.sleep(0.1)
            else:
                Fi = int(op.split()[2][1])
                events_for_snapshot[Fi].set()
                time.sleep(0.1)
            
        elif op.split()[0] == 'verify-transaction':
            if len(op.split()) !=2:
                print('Not a valid operation. Please input likes \'verify-transaciton <Fi>\'')
            Fi = int(op.split()[1][1])
            if len(Mined_Block_by_FullNode[Fi]) > 0:
                latest_block = Mined_Block_by_FullNode[Fi][-1]
                transactions = Block.find_txs(latest_block.Merkle)
                if len(transactions) > 0:
                    Latest_tx = transactions[-1]
                    if Latest_tx['tradeCnt'] > 0:
                        prev_tx = transactions_by_Vid[Latest_tx['Vid']][Latest_tx['tradeCnt']-1][0]
                        print('prev_Transaction\n->',prev_tx)
                        print('Latest_Transaction\n->',Latest_tx)
                        print(validate_transaction(prev_tx,Latest_tx))
                else:
                    print(Fi, '가 채굴 시도한 최신 block에 트랜잭션이 포함되지 않았습니다.',sep='')
            else:
                print(Fi,'가 채굴 시도한 Block이 아직 없습니다.',sep='')
        elif op.split()[0] == 'trace':
            if len(op.split()) !=2:
                print('Not a valid operation. Please input likes \'trace <Vid> ALL or <k>\'')
            Vid = op.split()[1]
            if Vid not in transactions_by_Vid.keys():
                print(Vid,'is not a valid Vid. There does not exist')
            elif op.split()[2]=='ALL':
                for transaction,blockHeight in reversed(transactions_by_Vid[Vid]):
                    print('in ',blockHeight)
                    print('\t',transaction,sep='')
            else:
                for transaction,blockHeight in reversed(transactions_by_Vid[Vid])[:int(op.split()[2])]:
                    print('in ',blockHeight)
                    print('\t',transaction,sep='')
        else:
            print('Wrong Operation.')

            print('to snapshot Fullnodes\' Blockchain:')
            print('Please input likes \'snapshot myBC ALL or <Fi>')

            print('to verify the Fullnode\'s last transaction:')
            print('Please input likes \'verify-transaciton <Fi>')

            print('to trace the Vehicle\'s tranding record: ')
            print('trace <Vid> ALL or <k>')
    '''
    for pipe_process in pipe_list:
        pipe_process.join()
    for usernode in usernodes:
        usernode.join()
    for fullnode in fullnode_process:
        fullnode.join()
    recv_thread.join()
    '''    
                
