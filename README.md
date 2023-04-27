# Azul AI Implementation

## Overview 
Use Min Max, Aplha Beta Pruning, and Monte carlo search trees along with associated herusitics to create AI agents for the 2-4 player baord game Azul. 

## Author
Pranathi Alluri and Yun Yi Park

## Running the game
```console
python run.py
```
In run.py 
#### Default: naive player vs naive player
players = [naive_player.NaivePlayer(0), naive_player.NaivePlayer(1)]
#### To run intereactive player: 
players = [iplayer.InteractivePlayer(0), naive_player.NaivePlayer(1)]
#### To run naive Minimax
minimax.MinMaxPlayer(0)
#### To run timed minimax
timed_minimax.TimedMinimax(0)
#### To run alpha beta pruning
alpha_beta.AlphaBeta(0)
#### To run alpha beta pruning with sort
alpha_beta_sort.SortedAlphaBeta(0)
#### To run Monte carlo Tree search:
players = [mctsPlayer.MctsPlayer(0), naive_player.NaivePlayer(1)]
#### To run multiple players:
Add a type of player to players list

Game frame forked from Michelle Blom's public repo. 
