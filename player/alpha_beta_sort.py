# Generate list of possible moves from current game state
# done 
# Create a child node / game state for each of the possible moves (by cloning the current state and playing the move)
# moves, game_state
# If at required depth: stop, otherwise repeat for each child node

import collections
import copy
import time
import numpy
from Player import Player
from utils import *
import math

class SortedAlphaBeta(Player):
    def __init__(self, id):
        super().__init__(id) 

    def get_available_tiles(self, game_state):
        bag = collections.defaultdict(int)  
        for tile in game_state.bag:
            bag[tile] += 1
        for factory in game_state.factories:
            for tile in range(5):
                bag[tile] += factory.tiles[tile]
        for tile in range(5):
            bag[tile] += game_state.centre_pool.tiles[tile]
        return bag 
    
    def estimate_bonus(self, game_State, player_state, round_num):
        row = self.estimate_extra_bonus(2, game_State, player_state, round_num, 'column')
        column = self.estimate_extra_bonus(7, game_State, player_state, round_num, 'row')
        set = self.estimate_extra_bonus(10, game_State, player_state, round_num, 'set')
        return player_state.EndOfGameScore() + row + column + set 
     
    def estimate_extra_bonus(self, bonus_point, game_state, player_state, round_num, flag):
        # Get the bag of tiles that the player has available
        bag = self.get_available_tiles(game_state)
        # Initialize the estimated bonus to 0
        estimated_bonus = 0 
        # Loop through each row or column (depending on the flag)
        for i in range(5):
            each_tile = 0
            vacant_unit = collections.defaultdict(int)
            for j in range(5):
                # Get the row, column, and tile type for the current spot
                if flag == 'row':
                    row_index = i
                    col_index = j
                    tile_type = player_state.grid_scheme[i][j]
                elif flag == 'col':
                    row_index = j
                    col_index = i
                    tile_type = player_state.grid_scheme[j][i]
                else:
                    row_index = j
                    col_index = i
                    tile_type = i

                # If there is a tile in the current spot in the column/row, increment the each_tile count
                if player_state.grid_state[row_index][col_index] == 1:
                    each_tile += 1
                # If there is no tile in the current spot in the column/row, increment the vacant_unit count
                elif player_state.grid_state[row_index][col_index] == 0:
                    already_placed = 0
                    # is the tile in the pattern line the tile that's needed to complete the row/column
                    if player_state.lines_tile[row_index] == tile_type:
                        # get the number of tiles in that pattern line 
                        already_placed = player_state.lines_number[row_index]
                    # add the count of vacant spots for that tile type by 
                    # subtracting the number of tiles that already exist in that pattern line 
                    # this is to avoid counting vacant spots that will be placed with the tiles in 
                    # the pattern line  
                    vacant_unit[int(tile_type)] += row_index + 1 - already_placed

            # Check if it's feasible to fill in the vacant spots using the bags and earn a bonus
            canFill = True
            for tile in vacant_unit.keys():
                if tile not in bag.keys() or vacant_unit[tile] > bag[tile]:
                    canFill = False

            # If it's feasible to earn a bonus, increment the estimated bonus score using the bonus unit
            if canFill:
                estimated_bonus += each_tile * bonus_point / 4

        # Apply a discount factor to the estimated bonus score based on the current round number, and return it
        estimated_bonus = estimated_bonus * 0.6 ** (4 - round_num)
        return estimated_bonus

    
    def place_in_center(self, plr_st): 
        final = 0
        CENTER_ROW = 2  
        CENTER_COLUMN = 2
        TOP = plr_st.grid_state[CENTER_ROW-1][CENTER_COLUMN]
        DOWN = plr_st.grid_state[CENTER_ROW+1][CENTER_COLUMN] == 1
        RIGHT = plr_st.grid_state[CENTER_ROW][CENTER_COLUMN+1] == 1
        LEFT = plr_st.grid_state[CENTER_ROW][CENTER_COLUMN-1] == 1
        TOP_RIGHT = plr_st.grid_state[CENTER_ROW-1][CENTER_COLUMN+1] == 1
        TOP_LEFT= plr_st.grid_state[CENTER_ROW-1][CENTER_COLUMN-1] == 1
        BOTTOM_RIGHT = plr_st.grid_state[CENTER_ROW+1][CENTER_COLUMN+1] == 1
        BOTTOM_LEFT= plr_st.grid_state[CENTER_ROW+1][CENTER_COLUMN-1] == 1

        if plr_st.grid_state[CENTER_ROW][CENTER_COLUMN] == 1: 
            final += 0.0005
        if TOP or DOWN or RIGHT or LEFT or TOP_RIGHT or TOP_LEFT or BOTTOM_RIGHT or BOTTOM_LEFT:
            final += 0.0003 
        return final


    def evalulate_function(self, game_state):  
        round_num = (4 - len(game_state.bag) // 20) 
        game_state_copy = copy.deepcopy(game_state)     

        # assume that round ends immediately 
        game_state_copy.ExecuteEndOfRound() 
        plr_state = game_state_copy.players[self.id]
        opponent_state = game_state_copy.players[self.id*-1 + 1] 

        # Feature 1: End of round score
        player_score = game_state_copy.players[self.id].score
        opponent_score = game_state_copy.players[opponent_state.id].score 

        # Feature 2: checks if the player has enough tiles in their bag to fill these vacancies
        player_bonus = self.estimate_bonus(game_state_copy, plr_state, round_num)
        opponent_bonus = self.estimate_bonus(game_state_copy, opponent_state, round_num)    

        # Feature 3: place close to the center
        player_place_in_center = self.place_in_center(plr_state)
        opponent_place_in_center = self.place_in_center(plr_state)               
        return (player_score - opponent_score) + (player_bonus - opponent_bonus)  +  (player_place_in_center - opponent_place_in_center)

    def filter(self, plr_st, moves):  

        if len(moves) > 7:  
            num_to_floor = move[2].num_to_floor_line 
            tile_type = move[2].tile_type
            pattern_line = move[2].pattern_line_dest
            num_to_line = move[2].num_to_pattern_line
            remainder =  0

            if plr_st.lines_tile[pattern_line] != -1: # there is a tile in the pattern line 
                already_exist = plr_st.lines_number[pattern_line] # how many tiles in the pattern line? 
                remainder = pattern_line + 1 - (already_exist + num_to_line) # how many empty spaces in the pattern line?
            else: 
                assert plr_st.lines_number[pattern_line] == 0 
                remainder = pattern_line + 1 - num_to_line 

            move_dict = {} 
            for move in moves:   
                unnecessary = remainder + num_to_floor
                numoffset = move[2].num_to_pattern_line - move[2].num_to_floor_line

                if (tile_type, pattern_line) not in move_dict or numoffset>move_dict[(tile_type, pattern_line)][0]:
                    move_dict[(tile_type, pattern_line)] = (numoffset, unnecessary, move)

            moves = [v[2] for k, v in sorted(move_dict.items(), key=lambda item: item[1][1])]

    def minimax(self, game_state, depth, start_time, end_time, maximizing=True):
        # game ends 
        game_end = False
        for plr_state in game_state.players:
            if plr_state.GetCompletedRows() > 0 :
                game_end = True
                break     
        # round ends
        round_end = False    
        if (game_state.TilesRemaining() == 0 and not game_end):
            round_end = True 

        # terminal node (when game_ends, round_ends, or when depth is 0)
        if game_end or round_end or depth == 0:
            value = self.evalulate_function(game_state)
            return (None, value)
        
        # maximize
        if maximizing:
            value = -math.inf
            moves = game_state.players[self.id].GetAvailableMoves(game_state)            
            best_move = moves[0]
            plr_state = game_state.players[self.id] 
            # only looking at most optimal moves
            filter(plr_state, moves)
            for move in moves: 
                if time.time() - start_time > end_time: return (best_move, value) 
                game_state_copy = copy.deepcopy(game_state)
                game_state_copy.ExecuteMove(self.id, move)                
                new_value = self.minimax(game_state_copy, depth-1,start_time, end_time, False)[1]
                if new_value > value:
                    value = new_value
                    best_move = move

            return best_move, value 
        
        # minimize
        else:
            value = math.inf
            moves = game_state.players[self.id*-1 + 1].GetAvailableMoves(game_state)
            best_move = moves[0]
            enemy_state = game_state.players[self.id*-1 + 1] 
            filter(enemy_state, moves) # only looking at most optimal moves
            for move in moves: 
                if time.time() - start_time > end_time: return (best_move, value) 
                game_state_copy = copy.deepcopy(game_state) 
                game_state_copy.ExecuteMove(self.id*-1 + 1, move)                
                new_value = self.minimax(game_state_copy, depth-1, start_time, end_time)[1]
                if new_value < value:
                    value = new_value
                    best_move = move 
            return best_move, value  
 
    def SelectMove(self, moves, game_state):
        start_time = time.time()
        best_move = None
        depth = 1
        max_depth = 10
        max_time = 3 
        for depth in range (1, max_depth):
            if time.time() - start_time > max_time: break 
            # print(time.time())
            best_value = -numpy.Infinity 
            move, value = self.minimax(game_state, depth, start_time, max_time, True)
            if value > best_value:
                best_value = value
                best_move = move
            depth += 1
        
        return best_move

