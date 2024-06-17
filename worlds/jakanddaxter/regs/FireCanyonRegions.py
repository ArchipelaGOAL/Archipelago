from ..Regions import Jak1Level, Jak1SubLevel
from ..locs import CellLocations as Cells, ScoutLocations as Scouts


class FireCanyon(Jak1Level):
    name = "Fire Canyon"
    total_orb_count = 50

    class MainArea(Jak1SubLevel):
        name = ""
        orb_count = 50

        def create_locations(self):
            self.create_cell_locations(Cells.locFC_cellTable)
            self.create_fly_locations(Scouts.locFC_scoutTable)

    def create_sub_levels(self):
        main = self.MainArea()

        self.sub_levels[main.name] = main
