
# Class representing a policy for playing AZUL.  
import random

import numpy

from utils import *

class Player(object):
    def __init__(self, _id):
        self.id = _id
        super().__init__()

    # Given a set of available moves for the player to execute, and
    # a copy of the current game state (including that of the player),
    # select one of the moves to execute. 
    def SelectMove(self, moves, game_state):
        return random.choice(moves)

# We use the PlayerState class to represent a player's game state:
# their score; the state of their pattern lines; the state of their
# wall grid; and their floor line.
class PlayerState:
    GRID_SIZE = 5
    FLOOR_SCORES = [-1,-1,-2,-2,-2,-3,-3]
    ROW_BONUS = 2
    COL_BONUS = 7
    SET_BONUS = 10

    def __init__(self, _id):
        self.id = _id
        self.score = 0
        self.lines_number = [0]*self.GRID_SIZE
        self.lines_tile = [-1]*self.GRID_SIZE

        self.player_trace = PlayerTrace(_id)

        #self.grid_scheme = [
        #    [Tile.BLUE,Tile.YELLOW,Tile.RED,Tile.BLACK,Tile.WHITE],
        #    [Tile.WHITE,Tile.BLUE,Tile.YELLOW,Tile.RED,Tile.BLACK],
        #    [Tile.BLACK,Tile.WHITE,Tile.BLUE,Tile.YELLOW,Tile.RED],
        #    [Tile.RED,Tile.BLACK,Tile.WHITE,Tile.BLUE,Tile.YELLOW],
        #    [Tile.YELLOW,Tile.RED,Tile.BLACK,Tile.WHITE,Tile.BLUE]
        #]
        self.grid_scheme = numpy.zeros((self.GRID_SIZE,self.GRID_SIZE))
        self.grid_scheme[0][Tile.BLUE] = 0
        self.grid_scheme[1][Tile.BLUE] = 1
        self.grid_scheme[2][Tile.BLUE] = 2
        self.grid_scheme[3][Tile.BLUE] = 3
        self.grid_scheme[4][Tile.BLUE] = 4

        self.grid_scheme[1][Tile.WHITE] = 0
        self.grid_scheme[2][Tile.WHITE] = 1
        self.grid_scheme[3][Tile.WHITE] = 2
        self.grid_scheme[4][Tile.WHITE] = 3 
        self.grid_scheme[0][Tile.WHITE] = 4
        
        self.grid_scheme[2][Tile.BLACK] = 0 
        self.grid_scheme[3][Tile.BLACK] = 1
        self.grid_scheme[4][Tile.BLACK] = 2
        self.grid_scheme[0][Tile.BLACK] = 3
        self.grid_scheme[1][Tile.BLACK] = 4

        self.grid_scheme[3][Tile.RED] = 0
        self.grid_scheme[4][Tile.RED] = 1
        self.grid_scheme[0][Tile.RED] = 2
        self.grid_scheme[1][Tile.RED] = 3
        self.grid_scheme[2][Tile.RED] = 4

        self.grid_scheme[4][Tile.YELLOW] = 0
        self.grid_scheme[0][Tile.YELLOW] = 1
        self.grid_scheme[1][Tile.YELLOW] = 2
        self.grid_scheme[2][Tile.YELLOW] = 3
        self.grid_scheme[3][Tile.YELLOW] = 4

        # Matrix representing state of the player's grid (ie. which
        # slots have tiles on them -- 1s -- and which don't -- 0s).
        self.grid_state = numpy.zeros((self.GRID_SIZE,self.GRID_SIZE))

        # State of the player's floor line, a 1 indicates there is
        # a tile sitting in that position in their floor line.
        self.floor = [0,0,0,0,0,0,0]
        self.floor_tiles = []

        # Record of the number of tiles of each colour the player
        # has placed in their grid (useful for end-game scoring)
        self.number_of = {}
        for tile in Tile:
            self.number_of[tile] = 0


    # Add given tiles to the player's floor line. After calling this 
    # method, 'tiles' will contain tiles that could not be added to
    # the player's floor line.
    def AddToFloor(self, tiles):
        number = len(tiles)
        for i in range(len(self.floor)):
            if self.floor[i] == 0:
                self.floor[i] = 1
                tt = tiles.pop(0)
                self.floor_tiles.append(tt)
                number -= 1
            if number == 0:
                break

    # Add given number of given tile type to the specified pattern line
    def AddToPatternLine(self, line, number, tile_type):
        assert line >= 0 and line < self.GRID_SIZE

        assert (self.lines_tile[line] == -1 or 
            self.lines_tile[line] == tile_type)

        self.lines_number[line] += number
        self.lines_tile[line] = tile_type

        assert self.lines_number[line] <= line + 1 


    # Assign first player token to this player
    def GiveFirstPlayerToken(self):
        for i in range(len(self.floor)):
            if self.floor[i] == 0:
                self.floor[i] = 1
                break


    # Compute number of completed rows in the player's grid
    def GetCompletedRows(self):
        completed = 0
        for i in range(self.GRID_SIZE):
            allin = True
            for j in range(self.GRID_SIZE):
                if self.grid_state[i][j] == 0:
                    allin = False
                    break
            if allin:
                completed += 1
        return completed

    
    # Compute number of completed columns in the player's grid
    def GetCompletedColumns(self):
        completed = 0
        for i in range(self.GRID_SIZE):
            allin = True
            for j in range(self.GRID_SIZE):
                if self.grid_state[j][i] == 0:
                    allin = False
                    break
            if allin:
                completed += 1
        return completed


    # Compute the number of completed tile sets in the player's grid
    def GetCompletedSets(self):
        completed = 0
        for tile in Tile:
            if self.number_of[tile] == self.GRID_SIZE:
                completed += 1
        return completed


    # Return the set of moves available to this player given the
    # current game state. 
    def GetAvailableMoves(self, game_state):
        moves = []

        # Look at each factory display with available tiles
        fid = 0
        for fd in game_state.factories:
            # Look at each available tile set
            for tile in Tile:
                num_avail = fd.tiles[tile]
            
                if num_avail == 0:
                    continue

                # A player can always take tiles, as they can be 
                # added to their floor line (if their floor line is 
                # full, the extra tiles are placed in the used bag).

                # First look through each pattern line, create moves 
                # that place the tiles in each appropriate line (with
                # those that cannot be placed added to the floor line).
                for i in range(self.GRID_SIZE):
                    # Can tiles be added to pattern line i?
                    # should be -1 or should be the same type of tile 
                    if self.lines_tile[i] != -1 and \
                        self.lines_tile[i] != tile:
                        # these tiles cannot be added to this pattern line
                        continue

                    # Is the space on the grid for this tile already
                    # occupied?
                    grid_col = int(self.grid_scheme[i][tile])
                    if self.grid_state[i][grid_col] == 1:
                        # It is, so we cannot place this tile type
                        # in this pattern line!
                        continue

                    # how many slots are free
                    # lines_number is the number of tiles that are already placed 
                    # for that pattern line 
                    slots_free = (i+1) - self.lines_number[i]
                    if slots_free == 0:
                        # if there are no slots to place the tile continue 
                        # to place it in the floor line
                        continue 
                    tg = TileGrab()
                    tg.number = num_avail
                    tg.tile_type = tile
                    tg.pattern_line_dest = i
                    # number of tiles to place in the pattern line 
                    tg.num_to_pattern_line = min(num_avail, slots_free)
                    # number of leftover tiles in the floor line 
                    tg.num_to_floor_line = tg.number - tg.num_to_pattern_line

                    moves.append((Move.TAKE_FROM_FACTORY, fid, tg))
        
                # Default move is to place all the tiles in the floor line
                tg = TileGrab()
                # number of tiles to take from factory 
                tg.number = num_avail 
                tg.tile_type = tile
                # number of tiles to place in the floor line
                tg.num_to_floor_line = tg.number  
                moves.append((Move.TAKE_FROM_FACTORY, fid, tg))

            fid += 1    

        # Alternately, the player could take tiles from the centre pool.
        # Note that we do not include the first player token in the 
        # collection of tiles recorded in each TileGrab. This is managed
        # by the game running class. 
        for tile in Tile:
            # Number of tiles of this type in the centre
            num_avail = game_state.centre_pool.tiles[tile]

            # if the there are no tiles of that type in the center pool 
            if num_avail == 0:
                continue

            # First look through each pattern line, create moves 
            # that place the tiles in each appropriate line (with
            # those that cannot be placed added to the floor line).
            for i in range(self.GRID_SIZE):
                # Can tiles be added to pattern line i?
                if self.lines_tile[i] != -1 and \
                    self.lines_tile[i] != tile:
                    # these tiles cannot be added to this pattern line
                    continue

                # Is the space on the grid for this tile already
                # occupied?
                grid_col = int(self.grid_scheme[i][tile])
                if self.grid_state[i][grid_col] == 1:
                    # It is, so we cannot place this tile type
                    # in this pattern line!
                    continue

                slots_free = (i+1) - self.lines_number[i]
                if slots_free == 0:
                        # if there are no slots to place the tile continue 
                        # to place it in the floor line
                        continue 
                tg = TileGrab()
                tg.number = num_avail
                tg.tile_type = tile
                tg.pattern_line_dest = i
                tg.num_to_pattern_line = min(num_avail, slots_free)
                tg.num_to_floor_line = tg.number - tg.num_to_pattern_line

                moves.append((Move.TAKE_FROM_CENTRE, -1, tg))
        
            # Default move is to place all the tiles in the floor line
            tg = TileGrab()
            tg.number = num_avail
            tg.tile_type = tile
            tg.num_to_floor_line = tg.number
            moves.append((Move.TAKE_FROM_CENTRE, -1, tg))

        return moves
         

    # Complete scoring process for player at round end: 
    # 1. Move tiles across from pattern lines to the grid and score each;
    #
    # 2. Clear remaining tiles on pattern lines (where appropriate) and
    # return to be added to "used" tiles bag;
    #
    # 3. Score penalties for tiles in floor line and return these tiles
    # to be added to the "used" tiles bag.
    #
    # Returns a pair: the change in the player's score; and the set of 
    # tiles to be returned to the "used" tile bag. The players internal
    # representation of their score is updated in the process. 
    def ScoreRound(self):
        used_tiles = []

        score_inc = 0

        # 1. Move tiles across from pattern lines to the wall grid
        for i in range(self.GRID_SIZE):
            # Is the pattern line full? If not it persists in its current
            # state into the next round.
            if self.lines_number[i] == i+1:
                tc = self.lines_tile[i]
                col = int(self.grid_scheme[i][tc])

                # Record that the player has placed a tile of type 'tc'
                self.number_of[tc] += 1

                # Clear the pattern line, add all but one tile into the
                # used tiles bag. The last tile will be placed on the 
                # players wall grid.  
                for j in range(i):
                    used_tiles.append(tc)

                self.lines_tile[i] = -1
                self.lines_number[i] = 0

                # Tile will be placed at position (i,col) in grid
                self.grid_state[i][col] = 1

                # count the number of tiles in a continguous line
                # above, below, to the left and right of the placed tile.
                above = 0
                for j in range(col-1, -1, -1): # iterates from col-1 -> 0 
                    val = self.grid_state[i][j]
                    above += val
                    if val == 0:
                        break
                below = 0
                for j in range(col+1,self.GRID_SIZE,1):
                    val = self.grid_state[i][j]
                    below +=  val
                    if val == 0:
                        break
                left = 0
                for j in range(i-1, -1, -1):
                    val = self.grid_state[j][col]
                    left += val
                    if val == 0:
                        break
                right = 0
                for j in range(i+1, self.GRID_SIZE, 1):
                    val = self.grid_state[j][col]
                    right += val
                    if val == 0:
                        break

                # If the tile sits in a contiguous vertical line of 
                # tiles in the grid, it is worth 1*the number of tiles
                # in this line (including itself).
                if above > 0 or below > 0:
                    score_inc += (1 + above + below)

                # In addition to the vertical score, the tile is worth
                # an additional H points where H is the length of the 
                # horizontal contiguous line in which it sits.
                if left > 0 or right > 0:
                    score_inc += (1 + left + right)

                # If the tile is not next to any already placed tiles
                # on the grid, it is worth 1 point.                
                if above == 0 and below == 0 and left == 0 \
                    and right == 0:
                    score_inc += 1

        # Score penalties for tiles in floor line
        penalties = 0
        for i in range(len(self.floor)):
            penalties += self.floor[i]*self.FLOOR_SCORES[i]
            self.floor[i] = 0
            
        used_tiles.extend(self.floor_tiles)
        self.floor_tiles = []
        
        # Players cannot be assigned a negative score in any round.
        score_change = score_inc + penalties
        if score_change < 0 and self.score < -score_change:
            score_change = -self.score
        
        self.score += score_change
        self.player_trace.round_scores[-1] = score_change

        return (self.score, used_tiles) 


    # Complete additional end of game scoring (add bonuses). Return
    # computed bonus, and add to internal score representation.
    def EndOfGameScore(self):
        rows = self.GetCompletedRows()
        cols = self.GetCompletedColumns()
        sets = self.GetCompletedSets()

        bonus = (rows * self.ROW_BONUS) + (cols * self.COL_BONUS) + \
            (sets * self.SET_BONUS)

        self.player_trace.bonuses = bonus
        self.score += bonus
        return bonus 
