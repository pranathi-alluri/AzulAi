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
            action = self.better_rollout_policy(possible_moves)
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

    def better_rollout_policy(self, moves):
        most_to_line = -1
        corr_to_floor = 0

        best_move = None

        for mid,fid,tgrab in moves:
            if most_to_line == -1:
                best_move = (mid,fid,tgrab)
                most_to_line = tgrab.num_to_pattern_line
                corr_to_floor = tgrab.num_to_floor_line
                continue

            if tgrab.num_to_pattern_line > most_to_line:
                best_move = (mid,fid,tgrab)
                most_to_line = tgrab.num_to_pattern_line
                corr_to_floor = tgrab.num_to_floor_line
            elif tgrab.num_to_pattern_line == most_to_line and \
                tgrab.num_to_pattern_line < corr_to_floor:
                best_move = (mid,fid,tgrab)
                most_to_line = tgrab.num_to_pattern_line
                corr_to_floor = tgrab.num_to_floor_line

        return best_move

    def backpropagate(self, result):
        self.visits += 1
        if result == 1:
            self.loses += 1
        else: 
            self.wins += 1
        if self.parent:
            self.parent.backpropagate(1 - result)










