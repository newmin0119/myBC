from hashlib import sha256
from ecdsa.keys import SigningKey,VerifyingKey
from ecdsa.util import sigencode_string,sigdecode_string

def HASH256(x):
    return sha256(sha256(x.encode()).hexdigest().encode()).hexdigest()

# 서명 생성 함수
def create_sig(sk,txid):
    message = bytes(txid.encode()) # byte 형식 message 샘플
    sig = sk.sign_deterministic(message,hashfunc=sha256,sigencode=sigencode_string)
    return sig

# 서명 인증 함수
def verify_sig(sig, pk_str, message) -> bool:
    '''
    ECDSA 기반 서명 검증 결과 -> bool
    ECDSA 기반 sig, pk로 검증
    '''
    pk = VerifyingKey.from_string(pk_str) # str에서 pubkey 보구
    return pk.verify(sig,message,sha256,sigdecode=sigdecode_string)