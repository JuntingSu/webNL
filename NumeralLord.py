__all__=[]

import json

PLAYER1, PLAYER2,PLAYER3,PLAYER4 = "red", "yellow","blue","black"

class NumeralLord:
    def __init__(self,map):
        mapfile = json.loads(map)
        self.moves = []
        self.terrain=mapfile["terrrain"]
        self.top = [0 for _ in range(7)]
        self.winner = None


    
