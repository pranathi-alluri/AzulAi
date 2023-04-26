import math
import numpy as np
import copy

class monteCarloNodes(object):
    def __init__ (self, player, game_state, parent=None, parent_move=None):
        self.player = player
        self.parent = parent
        self.parent_move = parent_move
        self.state = game_state
        self.children = []
        self.visits = 0
        self.next_moves = game_state.players[player].GetAvailableMoves(game_state)
        # self.next_moves = self.better_rollout_policy(self.unsorted_moves)
        self.wins = 0 
        self.loses = 0


    def get_parent_action(self):
        return self.parent_move

    def is_round_over(self):
        return not self.state.TilesRemaining()

    def q(self):
        return self.wins - self.loses

    def is_fully_expanded(self):
        return len(self.next_moves) == 0

    def get_best_child(self, c_param = 0.1):
        choice_weights = []
        for child in self.children:
            score = (child.q() / child.visits) + c_param * np.sqrt((2 * np.log(self.visits) / (child.visits)))
            choice_weights.append(score)

        best_child = self.children[np.argmax(choice_weights)]
        return best_child

    def expand(self):
        action = self.next_moves.pop(0)
        copy_state = copy.deepcopy(self.state)
        copy_state.ExecuteMove(self.player, action)
        child_node = monteCarloNodes(1 - self.player, copy_state, parent = self, parent_move = action)
        self.children.append(child_node)
        return child_node

    def rollout(self):
        next_player = self.player
        count = 0
        rollout_state = copy.deepcopy(self.state)
        current_player = rollout_state.players[self.player]
        opponent = rollout_state.players[1 - self.player]

        while rollout_state.TilesRemaining() and count < 3:
            possible_moves = rollout_state.players[next_player].GetAvailableMoves(rollout_state)
            # sorted_actions = self.better_rollout_policy(possible_moves)
            action = self.rollout_policy(possible_moves)
            rollout_state.ExecuteMove(next_player, action)
            count += 1
            next_player = 1 - next_player

        rollout_state.ExecuteEndOfRound()
        player_score = current_player.EndOfGameScore()
        opponent_score = opponent.EndOfGameScore()

        if player_score >= opponent_score:
            result = 1
        else:
            result = 0
        return result


    def rollout_policy(self, possible_moves):
        return possible_moves[np.random.randint(len(possible_moves))]

    def backpropagate(self, result):
        self.visits += 1
        if result == 1:
            self.loses += 1
        else: 
            self.wins += 1
        if self.parent:
            self.parent.backpropagate(1 - result) 

    '''
    def better_rollout_policy(self, possible_moves):
        sorted_moves = sorted(possible_moves, key= lambda x: (x[2].num_to_floor_line, -x[2].num_to_pattern_line))
        return sorted_moves 
    '''










