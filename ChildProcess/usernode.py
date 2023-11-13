import sys, os, time, random,string
from multiprocessing import Process
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

class UserNode(Process):
    def __init__(self,*args):
        super().__init__()
        car_num,write_pipe = args
        self.write_pipe = write_pipe
        self.my_Vehs = []
        """ 차 정보 정해진 개수만큼 랜덤하게 생성 """
        for _ in range(car_num):
            model,price = veh_models[random.randrange(1,6)]
            vid = ''.join(random.sample(letters_set,10))
            manufactured = str(randrange(1990,2024))+'.'+str(randrange(1,13))+'.'+str(randrange(1,28))
            self.my_Vehs.append((vid,model,price,manufactured))
        """ 타원 곡선: NIST P-192 curve 사용 """

    
    def __str__(self):
        myself = ''
        myself += 'my vehicles:'
        for veh in self.my_Vehs:
            myself+='\n'+str(veh)
        myself+= '\n'

        return myself

    def run(self,*args):
        txs_list = self.generate_transaction()
        for txs in txs_list:
            self.write_pipe.send(txs)
            time.sleep(15)

    def generate_transaction(self):
        keys = [[0]*6 for _ in range(len(self.my_Vehs))]
        txs = []
        for car in range(len(self.my_Vehs)):
            for i in range(6):
                keys[car][i] = SigningKey.generate()    # secret key
        
        
        # pk = sk.get_verifying_key()    # public key
        for i in range(5):
            txs.append([])
            for car in range(len(self.my_Vehs)):
                vid,model,price,manufactured = self.my_Vehs[car]
                tx = make_transaction(keys[car][i].get_verifying_key(),
                                      keys[car][i+1].get_verifying_key(),
                                      vid,
                                      model,
                                      i+1,
                                      price,
                                      manufactured
                                    )
                tx['sig'] = create_sig(keys[car][i],tx['txid'])
                txs[i].append(tx)
        return txs

### 예시 UserNode 및 트랜잭션 출력 ###
## u1 = UserNode(1,4)
## u1.generate_transaction(1)
### 예시 UserNode end ###