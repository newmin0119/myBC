import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from Blockchain.transaction import *
from Blockchain.Crpto_tools import *

class UserNode:
    def __init__(self,link_F) -> None:
        self.peer = link_F
        self.my_Vid = []