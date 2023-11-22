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

usernodes = []                  # Usernode Child Process를 담는 list
fullnodes = []                  # Fullnode Child Process를 담는 list
Master_from_full = []           # 각 Fullnode로부터 mining 결과를 받는 Pipe를 담는 list
events_for_snapshot = []        # 각 Fullnode에게 스냅샷 명령을 내리는 Event 를 담는 list
Mined_Block_by_FullNode = []    # 각 Fullnode로부터 받은 mining block을 순서대로 저장하는 list를 담는 list
transactions_by_Vid = dict()    # 각 채굴된 결과로부터 트랜잭션을 저장하는 Dictionary
                                #   key: Vid
                                #   value: List
                                #       각 list의 원소는 튜플 형태
                                #       ( 트랜잭션, 트랜잭션이 저장된 block의 height )


terminate_event = Event()       # exit 명령어 입력시 모든 Fullnode와 Usernode에게 종료를 알리는 Event 객체

def construct_P2P(N,M,genesis):
    '''
    가상 P2P Network를 구성하는 function
    매개변수 N과 M은 각각 fullnode의 수와 usernode의 수로 대응

    PRNG를 이용하여
        - 각 UserNode는 임의의 FullNode로         Pipe를 이용, 단방향 연결:    user_to_full, full_from_user
        - 각 FullNode는 임의의 다른 FullNode로     이중 Pipe를 이용, 양방향 연결:  full_to_full   
        - 그리고 모든 FullNode는 MasterProcess로   Pipe를 이용, 단방향 연결:   full_to_master, mastter_from_full

    이후, 생성된 Pipe와 필요한 Event 객체를 각각 User와 Full Node class로 argument로 전달
    또한, Master Process에서도 Read Pipe를 유지하여 Full Node로부터 Data를 넘겨 받음

    PRNG 사용 방법
        1) 각 Usernode는 생성된 Fullnode 중 랜덤하게 하나의 Fullnode를 채택하여 연결된다
            -> 따라서 어떠한 Usernode와도 연결되지 않은 Fullnode가 존재할 가능성이 있다.
        2) 각 Fullnode는 생성된 다른 Fullnode와 개별적으로 50%의 확률로 연결되거나 되지 않는다
            -> 따라서 모든 Fullnode가 연결되지 않을 수 있다.
            -> 이 경우, 독립적인 여러개의 Consensus Chain을 가진 Network가 구성된다.
        하지만,
        => 1번의 경우 Fullnode보다 압도적으로 많은 Usernode인 기존의 Bitcoin Network의 특성과
        => 2번의 경우 Fullnode가 충분히 많은 수가 유지되는 기존의 Bitcoin Network의 특성이 조합된다면
        평균적으로 모든 node가 하나의 Chain으로 연결되게 되고, 모든 채굴 노드는 충분한 수의 연결된 유저노드를 가지게 된다.
    '''
    user_to_full = []
    full_from_user = [list() for _ in range(N)]
    full_to_full = [list() for _ in range(N)]
    full_to_Master = []
    
    # User <-> Full 구성
    for user_num in range(M):
        full_num = randint(0,N-1)
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
        usernodes.append(UserNode(user_num,randint(1,3),user_to_full[user_num],terminate_event))

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
                                    event_for_snapshot,
                                    terminate_event
                                )
                        )
def listen_Block(pipe,q):
    while True:
        recv_block = pipe.recv()
        q.put(recv_block)
        if recv_block[0]==-1:
            pipe.close()
            break

def gather_block(q,N):
    global Mined_Block_by_FullNode
    count_terminate = 0
    while count_terminate<N:
        Fi, tempblock = q.get()
        if Fi==-1:
            count_terminate+=1
            continue
        print('\033[32ma block with blockHeight %d mined by F%d(report arrived at %s)' 
              % (tempblock.Header['blockHeight'], Fi, time.strftime('%H:%M:%S', time.localtime(time.time()))) + '\033[0m')
        Mined_Block_by_FullNode[Fi].append(tempblock)
        transactions = Block.find_txs(tempblock.Merkle)
        for transaction in transactions:
            transaction = eval(transaction)
            if transaction['Vid'] not in transactions_by_Vid.keys():
                transactions_by_Vid[transaction['Vid']] = []
            transactions_by_Vid[transaction['Vid']].append((transaction,tempblock.Header['blockHeight']))

def transaction_fixed_attributes(tx):
    ret =   '\n\t\033[33mVid: \033[0m'+ tx['Vid']
    ret +=  '\n\t\033[33mtradeCnt: \033[0m'+ str(tx['tradeCnt'])
    ret +=  '\n\t\033[33mmodelName: \033[0m'+ tx['modelName']
    ret +=  '\n\t\033[33mmanufacturedTime: \033[0m'+ tx['manufacturedTime']
    ret +=  '\n\t\033[33mprice: \033[0m'+ str(tx['price'])
    return ret

def verify_transaction(Fi):
    if len(Mined_Block_by_FullNode[Fi]) > 0:
        latest_block = Mined_Block_by_FullNode[Fi][-1]
        transactions = Block.find_txs(latest_block.Merkle)
        if len(transactions) > 0:
            Latest_tx = eval(transactions[-1])
            print('\033[34m--------------------------------------------')
            print('\033[32mtrID: \033[0m'+ Latest_tx['txid'])
            if Latest_tx['tradeCnt'] > 1:
                prev_tx = transactions_by_Vid[Latest_tx['Vid']][Latest_tx['tradeCnt']-1][0]
                print('\033[32mLast Transaction\'s output:      \033[0m',str(prev_tx['output']))
                print('\033[32mMost Recent Transaction\'s input:\033[0m',str(Latest_tx['input']))
                print('\033[32mLast transaction\'s\033[0m', transaction_fixed_attributes(prev_tx))
                print('\033[32mMost Recent Transaction\'s\033[0m', transaction_fixed_attributes(Latest_tx))
                print('\033[32mtrID\'s signature: \033[0m'+str(Latest_tx['sig']))
                print('\033[32mverifying using trID’s input: : \033[0m'+str(Latest_tx['input']))
                print('\033[32mVerify Result: \033[0m', validate_transaction(prev_tx,Latest_tx))
            else:
                print('\033[32mMost Recent Transaction is first trade in that Vid\033[0m')
                print('\033[32mMost Recent Transaction\'s\033[0m', transaction_fixed_attributes(Latest_tx))
                print('\033[32mverifying using trID’s input: : \033[0m'+ str(Latest_tx['input']))
                print('\033[32mVerify Result: \033[0m', validate_transaction(None,Latest_tx))
            print('\033[34m--------------------------------------------\033[0m')
        else:
            print('\033[95mF',Fi, '가 채굴 시도한 최신 block에 트랜잭션이 포함되지 않았습니다.\033[0m',sep='')
    else:
        print('\033[95mF',Fi,'가 채굴 시도한 Block이 아직 없습니다.\033[0m',sep='')

def trace_vid(Vid,keyword):
    if Vid not in transactions_by_Vid.keys():
        print('\033[95m',Vid,' is not a valid Vid. There does not exist\033[0m',sep='')
    elif keyword=='ALL':
        for transaction,blockHeight in reversed(transactions_by_Vid[Vid]):
            print('\033[34m--------------------------------------------')
            print('\033[32min blockHeight \033[0m',blockHeight)
            for tx_attribute in transaction.keys():
                print('\t\033[33m', tx_attribute,': \033[0m', transaction[tx_attribute],sep='')
            print('\033[34m--------------------------------------------\033[0m')
    else:
        k = keyword
        for transaction,blockHeight in reversed(transactions_by_Vid[Vid][-k:]):
            print('\033[34m--------------------------------------------')
            print('\033[32min blockHeight \033[0m',blockHeight)
            for tx_attribute in transaction.keys():
                print('\t\033[33m', tx_attribute,': \033[0m', transaction[tx_attribute],sep='')
            print('\033[34m--------------------------------------------\033[0m')

if __name__=='__main__':
    """
    This is main code
    Manager object can control All the Child Process
    And also it has N+1 threads. 
        N == the number of Fullnodes
    1) Receive_block Thread 
        - Print Mining record
    Listen_Block Thread
        - Listening Block from pipe which is connected with Fi
    And also it has 4 another actions
    2) Snapshot myBC <ALL> or <Fi>.
        - When excute with 'ALL', print longest chains that all the FullNodes thinks of as correct.
        - When excute with <Fi>, print a longest chain that the specified FullNode think of as correct.
            -> 0 <= i <= N-1, when N FullNodes exist.
    3) Verify-transaction <Fi>
        - Print the last transaction in the most recent Block <Fi> tried to mine.
        - And also print the result of verification.
    4) Trace <Vid> 'All' or <k>
        - When excute with 'ALL', print all transactions for specified vehicle.
        - When excute with <k>, print k transactions for specified vehicle from the first.
    5) exit
        - It set the terminate_event
        - And All the Child Processes can notice that
        - then, they will be terminated soon
    """
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
    
    gather_thread = Thread(target=gather_block,args=(q,N,))
    gather_thread.start()
    while True:
        op = input()
        if op=='exit':
            terminate_event.set()
            for event in events_for_snapshot:
                    event.set()
            for pipe_process in pipe_list:
                pipe_process.join()
            print("pipe_process - terminate")
            for usernode in usernodes:
                usernode.join()
            print("usernodes - terminate")
            for fullnode in fullnode_process:
                fullnode.join()
            print("fullnodes - terminate")
            gather_thread.join()
            print('recv_thread - terminate')
            break
            
        elif op.split()[0]=='snapshot':
            if len(op.split()) !=3:
                print('\033[95mNot a valid operation. Please input likes \'snapshot myBC ALL or <Fi>\'\033[0m')
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
                print('\033[95mNot a valid operation. Please input likes \'verify-transaciton <Fi>\'\033[0m')
                continue
            Fi = int(op.split()[1][1])
            verify_transaction(Fi)
        elif op.split()[0] == 'trace':
            if len(op.split()) !=3:
                print('\033[95mNot a valid operation. Please input likes \'trace <Vid> ALL or <k>\'\033[95m')
                continue
            Vid = op.split()[1]
            keyword = op.split()[2]
            if keyword != 'ALL':
                keyword = int(keyword)
            trace_vid(Vid,keyword)
        else:
            print('\033[95mWrong Operation.\033[95m')

            print('\033[95mto snapshot Fullnodes\' Blockchain:')
            print('\033[0mPlease input likes \033[33m\'snapshot myBC ALL or <Fi>\033[0m')

            print('\033[95mto verify the Fullnode\'s last transaction:')
            print('\033[0mPlease input likes \033[33m\'verify-transaciton <Fi>')

            print('\033[95mto trace the Vehicle\'s tranding record: ')
            print('\033[0mPlease input likes \033[33mtrace <Vid> ALL or <k>\033[0m')
    
    print('bye')
