from hashlib import sha256
from ecdsa.keys import SigningKey,VerifyingKey
from ecdsa.util import sigencode_string,sigdecode_string

def HASH256(x):
    return sha256(sha256(x.encode()).hexdigest().encode()).hexdigest()

# 서명 인증 함수 -- 구현필요
def verify_sig(sig, pk_str, message):
    '''
    ECDSA 기반 서명 검증 결과 -> message (str)
    ECDSA 기반 sig, pk로 검증
    '''
    pk = VerifyingKey.from_string(pk_str) # str에서 pubkey 보구
    return pk.verify(sig,message,sha256,sigdecode=sigdecode_string)
    # message 반환형태 가공