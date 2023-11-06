from hashlib import sha256
from OpenSSL.crypto import _EllipticCurve


def HASH256(x):
    return sha256(sha256(x.encode()).hexdigest().encode()).hexdigest()

# 서명 인증 함수 -- 구현필요
def verify_sig(self, sig, pk):
    # ECDSA 기반 서명 검증 결과 -> message (str)
    message = ''
    # ECDSA 기반 sig, pk로 검증
    # message 반환형태 가공
    return message