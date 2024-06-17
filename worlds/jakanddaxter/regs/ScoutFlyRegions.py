from ..Regions import Jak1Level, Jak1SubLevel
from ..locs import CellLocations as Cells

# This is a virtual location, it's not anywhere in the game.
# It just needs to exist as a Region attached to the "Menu" Region
# so that Archipelago can give you these Cells any time, anywhere,
# when you receive the 7th scout fly for an area.
class ScoutFlyCells(Jak1Level):
    name = "'Free 7 Scout Flies' Cells"
    total_orb_count = 0

    class MainArea(Jak1SubLevel):
        name = ""
        orb_count = 0

        def create_locations(self):
            self.create_cell_locations(Cells.loc7SF_cellTable)

    def create_sub_levels(self):
        main = self.MainArea()

        self.sub_levels[main.name] = main
