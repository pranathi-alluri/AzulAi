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
from model import GameRunner,Player
from player import iplayer
from player import naive_player

from player import minimax
from player import timed_minimax
from player import alpha_beta_sort
from player import alpha_beta
from player import mctsPlayer
from utils import *




players = [timed_minimax.TimedMinimax(0), mctsPlayer.MctsPlayer(1)]
gr = GameRunner(players, 1384754856864)
activity = gr.Run(True)  
print("Player 0 score is {}".format(activity[0][0]))
print("Player 1 score is {}".format(activity[1][0]))

# print("Player 2 score is {}".format(activity[2][0]))
# print("Player 3 score is {}".format(activity[3][0]))

#print("Player 0 round-by-round activity")
#player_trace = activity[0][1]
#for r in range(len(player_trace.moves)):
#    print("ROUND {}".format(r+1))
#    for move in player_trace.moves[r]:
#        print(MoveToString(0, move))
#    print("Score change {}".format(player_trace.round_scores[r]))

#print("Bonus points {}".format(player_trace.bonuses))
