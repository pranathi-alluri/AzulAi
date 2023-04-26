
from Player import Player
from model import *
from utils import *
from player.montecarlonodes import monteCarloNodes
from player.montecarlosearch import MCTS

class MctsPlayer(Player):
    def __init__(self,_id):
        super().__init__(_id)

    def SelectMove(self, move, game_state):
        root = monteCarloNodes(self.id, game_state, parent=None, parent_move=None)
        selected_node = MCTS(root)
        best_move = selected_node.best_action(300)
        return best_move
