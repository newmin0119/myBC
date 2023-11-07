import sys, os, time, random,string
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

#from Blockchain.transaction import *
from ecdsa.keys import SigningKey,VerifyingKey
from Blockchain.transaction import make_transaction
randrange = random.randrange

veh_models = [
    ('Genesis_GV80',70000),
    ('Porsche_panamera4',150000),
    ('Mercedes_Benz_Sonderklasse',170000),
    ('Bentley_continental_GT',330000),
    ('Rolls_Royce_Ghost',510000),
    ('Lamborghini_Aventador_svj',680000)
]
letters_set = string.ascii_letters+string.digits

class UserNode:
    def __init__(self,link_F,cars) -> None:
        self.peer = link_F
        self.my_Vehs = []
        """ 차 정보 정해진 개수만큼 랜덤하게 생성 """
        for i in range(cars):
            model,price = veh_models[random.randint(6)]
            vid = ''.join(random.sample(letters_set,10))
            manufactured = str(randrange(1990,2024))+'.'+str(randrange(1,13))+'.'+str(randrange(1,28))
            self.my_Vehs.append((vid,model,price,manufactured))
        """ 타원 곡선: NIST P-192 curve 사용 """
        self.sk = SigningKey.generate()     # secret key
        self.pk = self.sk.verifying_key     # public key
    
    def generate_transaction(self,dest):
        '''
        dest는 임시로 생성.
        추후 임의로 유저노드 선택하는 코드 추가
        '''
        for vid,model,price,manufactured in self.my_Vid:
            tx = make_transaction(self.pk,dest,Vid=vid,modelName=model,tradeCnt=1,price=price,manufacturedTime=manufactured)
            ''' ipc로 tx self.peer에게 전달'''
    
    def listen():
        '''
        인접 fullnode로 부터 output의 pubkey가 나와 일치하는 트랜잭션 수신
        나의 utxo set에 저장
        이후 15초 이후에 전달 -> 아마 generate_transaction으로 구현
        '''
        pass
    