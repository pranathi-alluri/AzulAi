# We use the tile display class to represent both factory displays and 
# the pool of tiles in the centre of the playing area. 
from utils import Tile


class TileDisplay:
    def __init__(self):
        # Map between tile colour and number in the display
        self.tiles = {}

        # Total number of tiles in the display
        self.total = 0

        for tile in Tile:
            self.tiles[tile] = 0

    def RemoveTiles(self, number, tile_type):
        assert number > 0
        assert tile_type in Tile
        assert tile_type in self.tiles

        self.tiles[tile_type] -= number
        self.total -= number

        assert self.tiles[tile_type] >= 0
        assert self.total >= 0

    def AddTiles(self, number, tile_type):
        assert number > 0
        assert tile_type in Tile
        assert tile_type in self.tiles
        
        self.tiles[tile_type] += number
        self.total += number


