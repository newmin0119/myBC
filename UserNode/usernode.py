import sys, os, time, random,string
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from ecdsa.keys import SigningKey,VerifyingKey
from Blockchain.transactions import make_transaction
from Blockchain.Crypto_tools import create_sig
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
    def __init__(self,car_num) -> None:
        self.my_Vehs = []
        """ 차 정보 정해진 개수만큼 랜덤하게 생성 """
        for _ in range(car_num):
            model,price = veh_models[random.randrange(1,6)]
            vid = ''.join(random.sample(letters_set,10))
            manufactured = str(randrange(1990,2024))+'.'+str(randrange(1,13))+'.'+str(randrange(1,28))
            self.my_Vehs.append((vid,model,price,manufactured))
        """ 타원 곡선: NIST P-192 curve 사용 """
        self.sk = SigningKey.generate()     # secret key
        self.pk = self.sk.get_verifying_key()    # public key
    
    def generate_transaction(self,dest):
        txs = []
        for vid,model,price,manufactured in self.my_Vehs:
            tx = make_transaction(self.pk,dest,Vid=vid,modelName=model,tradeCnt=1,price=price,manufacturedTime=manufactured)
            tx['sig'] = create_sig(self.sk,tx['txid'])
            txs.append(tx)
        return txs

### 예시 UserNode 및 트랜잭션 출력 ###
## u1 = UserNode(1,4)
## u1.generate_transaction(1)
### 예시 UserNode end ###