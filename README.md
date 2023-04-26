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
### Default: naive player vs naive player
players = [naive_player.NaivePlayer(0), naive_player.NaivePlayer(1)]
### To run intereactive player: 
players = [iplayer.InteractivePlayer(0), naive_player.NaivePlayer(1)]
### To run Monte carlo Tree search:
players = [mctsPlayer.MctsPlayer(0), naive_player.NaivePlayer(1)]
### To run multiple players:
Add a type of player to players list

Game frame forked from Michelle Bloom's public repo. 
