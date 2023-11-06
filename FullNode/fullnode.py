import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from Blockchain.transaction import *
from Blockchain.Crpto_tools import *
from Blockchain.Block import *


class FullNode:
    """
    A class of FullNode, generated by MasterProcess

    """
    # 클래스 최초 생성 함수
    def __init__(self,genesisBlock,target_N) -> None:
        self.longest_chain = [genesisBlock]
        self.tx_pool = []
        self.target_N = target_N
    
    # 트랜잭션 인증 함수
    @classmethod
    def validate_transactions(self, txs) -> bool:
        n = len(txs)
        for i in range(1,n):
            ## 1) txs(k)'s buyer == txs(k-1)'s seller
            if txs[i]['input']!=txs[i-1]['output']: return False
            
            ## 2) Check immutable value
            if txs[i]['Vid']!=txs[i-1]['Vid']: return False
            if txs[i]['modelName']!=txs[i]['modelName']: return False
            if txs[i]['manufacturedTime']!=txs[i]['manufacturedTime']: return False

            ## 3) Verify signature
            if txs[i-1]['txid']!= verify_sig(txs[i]['sig'],txs[i]['input']): return False
        
        return True

    # 채굴 함수
    def mining_process(self):
        """
        Mining process
        """
        header = {
            'blockHeight': self.longest_chain[-1].blockHeight+1,
            'prevHash': self.longest_chain[-1],
            'nonce': '',
            'Merkle-root': ''
        }
        # set_merkle 함수 활용 merkle 생성
        set_merkle(self.tx_pool) # -- pool 추후 집합으로 변경 필요
        # nonce 값 조정, nonce<=self.target_N
        # 
        while 1: pass

    # 트랜잭션 받는 함수
    # from UserNode
    def listen_transaction(self,tx):
        if self.validate_transactions(tx):
            self.tx_pool.append(tx)
    
    # 채굴된 블락 받는 함수
    # from MasterProcess
    def listen_Block(self,block):
        if self.validate_transactions(block):
            # Mining process 중지
            self.longest_chain.append(block)
            # 그 다음 Mining 시작