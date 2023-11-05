import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from Blockchain.transaction import *
from OpenSSL.crypto import _EllipticCurve

# 서명 인증 함수 -- 구현필요
def verify_sig(sig, pk):
    # ECDSA 기반 서명 검증 결과 -> message (str)
    message = ''
    # ECDSA 기반 sig, pk로 검증
    # message 반환형태 가공
    return message

# 트랜잭션 인증 함수
def validate_transactions(txs) -> bool:
    
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
