# Written by Michelle Blom, 2019
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
from AZUL.GameState import GameState
from utils import *

import numpy
import random
import abc
import copy

# Class that facilities a simulation of a game of AZUL. 
class GameRunner:
    def __init__(self, player_list, seed):
        random.seed(seed)

        # Make sure we are forming a valid game, and that player
        # id's range from 0 to N-1, where N is the number of players.
        assert(len(player_list) <= 2)
        assert(len(player_list) > 1)

        i = 0
        for plyr in player_list:
            assert(plyr.id == i)    
            i += 1

        self.game_state = GameState(len(player_list))
        self.players = player_list


    def Run(self, log_state):
        player_order = []
        for i in range(self.game_state.first_player, len(self.players)):
            player_order.append(i)

        for i in range(0, self.game_state.first_player):
            player_order.append(i)

        game_continuing = True
        for plr in self.game_state.players:
            plr.player_trace.StartRound()

        while game_continuing:
            for i in player_order:
                plr_state = self.game_state.players[i]
                moves = plr_state.GetAvailableMoves(self.game_state)

                gs_copy = copy.deepcopy(self.game_state)
                moves_copy = copy.deepcopy(moves)
                selected = self.players[i].SelectMove(moves_copy, gs_copy)

                assert(ValidMove(selected, moves))

                if log_state:
                    print("\nPlayer {} has chosen the following move:".format(
                        i))
                    print(MoveToString(i, selected))
                    print("\n")

                self.game_state.ExecuteMove(i, selected)
                if log_state:
                    print("The new player state is:")
                    print(PlayerToString(i, plr_state))

                if not self.game_state.TilesRemaining():
                    break

            # Have we reached the end of round?
            if self.game_state.TilesRemaining():
                continue

            # It is the end of round
            if log_state:
                print("ROUND HAS ENDED")

            self.game_state.ExecuteEndOfRound()

            # Is it the end of the game? 
            for i in player_order:
                plr_state = self.game_state.players[i]
                completed_rows = plr_state.GetCompletedRows()

                if completed_rows > 0:
                    game_continuing = False
                    break

            # Set up the next round
            if game_continuing:
                self.game_state.SetupNewRound()
                player_order = []
                for i in range(self.game_state.first_player,len(self.players)):
                    player_order.append(i)

                for i in range(0, self.game_state.first_player):
                    player_order.append(i)
                

        if log_state:
            print("THE GAME HAS ENDED")

        # Score player bonuses
        player_traces = {}
        for i in player_order:
            plr_state = self.game_state.players[i]
            plr_state.EndOfGameScore()
            player_traces[i] = (plr_state.score, plr_state.player_trace)
    
        # Return scores
        return player_traces
