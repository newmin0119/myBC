from hashlib import sha256
from ecdsa.keys import SigningKey,VerifyingKey
from ecdsa.util import sigencode_string,sigdecode_string

def HASH256(x):
    # sha256을 두 번 거친 결과를 16진수 표기법으로 반환하는 함수
    return sha256(sha256(x.encode()).hexdigest().encode()).hexdigest()

# 서명 생성 함수
def create_sig(sk,m):
    # secret key, 즉 Private Key를 통해 message를 서명하여 signature를 생성 및 반환하는 함수
    message = bytes(m.encode()) # byte 형식 message 샘플
    sig = sk.sign_deterministic(message,hashfunc=sha256,sigencode=sigencode_string)
    return sig

# 서명 인증 함수
def verify_sig(sig, pk, m) -> bool:
    '''
    ECDSA 기반 서명 검증 결과 -> bool
    ECDSA 기반 sig, pk로 검증
    '''
    message = bytes(m.encode())
    return pk.verify(sig,message,sha256,sigdecode=sigdecode_string)
