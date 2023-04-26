from player.montecarlonodes import *

class MCTS(object):
    def __init__(self, node: monteCarloNodes):
        self.root = node

    def traverse(self):
        current = self.root
        while not current.is_round_over():
            if not current.is_fully_expanded():
                return current.expand()
            else:
                current = current.get_best_child()

        return current

    def best_action(self, simulations_number):
        for i in range(simulations_number):
            v = self.traverse()
            reward = v.rollout()
            v.backpropagate(reward)

        return self.root.get_best_child(c_param=0.0).get_parent_action()


