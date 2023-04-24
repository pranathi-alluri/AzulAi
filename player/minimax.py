# Generate list of possible moves from current game state
# done 
# Create a child node / game state for each of the possible moves (by cloning the current state and playing the move)
# moves, game_state
# If at required depth: stop, otherwise repeat for each child node

import collections
import copy
from numpy import Infinity
import numpy
from Player import Player

class MinMaxPlayer(Player):
    def __init__(self, id):
        super().__init__(id)

    # # num of tiles 
    # def get_grid_tileCnt(self, game_state):
    #     player_grid_tiles =0
    #     opponent_grid_tiles =0

    #     plr_state = game_state.players[self.id]
    #     opponent_state = game_state.players[self.id*-1 + 1]  

    #     player_tile_exist = 0
    #     opponent_tile_exist = 0

    #     for i in range(plr_state.GRID_SIZE):
    #         player_tile_exist += plr_state.lines_number[i]

    #         for j in range(plr_state.GRID_SIZE):                    
    #             if plr_state.grid_state[i][j] != 0: 
    #                 player_grid_tiles+=1    

    #     for i in range(opponent_state.GRID_SIZE):
    #         opponent_tile_exist += opponent_state.lines_number[i]

    #         for j in range(5):                    
    #             if opponent_state.grid_state[i][j] != 0: 
    #                 opponent_grid_tiles+=1         

    #     return (player_grid_tiles - opponent_grid_tiles) - (player_tile_exist - opponent_tile_exist)

    def get_bag(self, game_state):
        bag_dic = collections.defaultdict(int) 
        for tile in game_state.bag:
            bag_dic[tile] += 1

        for factory in game_state.factories:
            for tile in range(5):
                bag_dic[tile] += factory.tiles[tile]

        for tile in range(5):
            bag_dic[tile] += game_state.centre_pool.tiles[tile]

        return bag_dic
    
    def get_bonus(self, bonus_unit, game_state, player_state, round_num, flag):
        bag_dic = self.get_bag(game_state)
        estimated_bonus = 0

        for i in range(5):
            each_unit = 0
            vacant_unit = collections.defaultdict(int)
            for j in range(5):
                if flag == 'row':
                    row_index = i
                    column_index = j
                    tile_type = numpy.where(player_state.grid_scheme[i] == j)[0]
                elif flag == 'col':
                    row_index = j
                    column_index = i
                    tile_type = numpy.where(player_state.grid_scheme[j] == i)[0]
                else: #set
                    row_index = j
                    column_index = int(player_state.grid_scheme[j][i])
                    tile_type = i

                if player_state.grid_state[row_index][column_index] == 1:
                    each_unit += 1
                elif player_state.grid_state[row_index][column_index] == 0:
                    left = 0
                    if player_state.lines_tile[row_index] == tile_type:
                        left = player_state.lines_number[row_index]
                    vacant_unit[int(tile_type)] += row_index + 1 - left

            feasible = True        

            for tile in vacant_unit.keys():
                if not tile in bag_dic.keys() or vacant_unit[tile] > bag_dic[tile]:
                        feasible = False
        
            if each_unit >= round_num and feasible:
                estimated_bonus += each_unit * bonus_unit/5

        estimated_bonus = estimated_bonus*0.9**(4-round_num) 
        return estimated_bonus
    
    # estimates the bonus points if this round were to be the last round
    def bonus_estimates(self, game_state, player_state, round_num):
        row_score = self.get_bonus(2, game_state, player_state, round_num, 'row')
        column_score = self.get_bonus(7, game_state, player_state, round_num, 'col')
        set_score = self.get_bonus(10, game_state, player_state, round_num , 'set')
        return row_score + column_score + set_score 

    def evaluate(self, game_state):
        # evaluate player score assuming that the round ends now

        round_num = (4 - len(game_state.bag) // 20) 
        game_state_copy = copy.deepcopy(game_state)        

        # get opponent id to get the opponent's current game state 
        opponent_id = self.id*-1 + 1
        # declare the end of round 
        game_state_copy.ExecuteEndOfRound() 
        # what's the score after the end of the round for each player?
        player_score = game_state_copy.players[self.id].score
        opponent_score = game_state_copy.players[opponent_id].score

        # bonus points for the player and opponent for the current game state 
        plr_state = game_state_copy.players[self.id]
        opponent_state = game_state_copy.players[opponent_id]    
        player_bonus = self.get_estimated_bonus(game_state_copy, plr_state, round_num)
        opponent_bonus = self.get_estimated_bonus(game_state_copy, opponent_state, round_num)

        # difference = self.get_grid_tileCnt(game_state_copy)       

        return (player_score - opponent_score) + (player_bonus - opponent_bonus)  


    def minimax(self, game_state, depth, maximizingPlayer=True):
        # define terminal state 
        is_terminal = False
        for plr_state in game_state.players:
            if plr_state.GetCompletedRows() > 0 :
                is_terminal = True
                break

        # end of round, but not end of game 
        is_round_end = False
        if not is_terminal and game_state.TilesRemaining() == 0:
            is_round_end = True     

        # terminal node 
        if depth == 0 or is_terminal or is_round_end:
            return self.evalulate(game_state)

        # each node is the available moves for that player 
        moves = game_state.players[self.id].GetAvailableMoves(game_state) 
        plr_state = game_state.players[self.id]
        bestValue = -Infinity
        
        # if it's the maiximizing player's turn
        if maximizingPlayer:
            for move in moves:
                game_state_copy = copy.deepcopy(game_state)
                game_state_copy.ExecuteMove(self.id, move)
                value = self.minimax(game_state_copy, depth - 1, False)
                bestValue = max(bestValue, value)
            return bestValue
        
        # minimizing player's turn
        else:
            bestValue = +Infinity
            for move in moves:
                game_state_copy = copy.deepcopy(game_state)
                game_state_copy.ExecuteMove(self.id, move)
                value = self.minimax(game_state_copy, depth - 1, False)
                bestValue = min(bestValue, value)
            return bestValue
        
    def SelectMove(self, moves, game_state):
        # Select moves based on min-max algorithm, where the AI 
        # aims to maximize the total scores for each round 
        depth = 4

        if len(moves) >55:
            depth = 3
        elif len(moves) >10:
            depth = 4
        else :
            depth = 5

        for move in moves: 
            best_value = -Infinity
            best_move = None
            value = self.minimax(game_state, depth, True)
            if value > best_value:
                value = best_value 
                best_move = move

        return best_move

