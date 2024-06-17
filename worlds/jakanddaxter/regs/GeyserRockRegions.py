from ..Regions import Jak1Level, Jak1SubLevel
from ..locs import CellLocations as Cells, ScoutLocations as Scouts


class GeyserRock(Jak1Level):
    name = "Geyser Rock"
    total_orb_count = 50

    class MainArea(Jak1SubLevel):
        name = "Main Area"
        orb_count = 50

        def create_locations(self):
            self.create_cell_locations({k: Cells.locGR_cellTable[k] for k in {92, 93}})
            self.create_fly_locations(Scouts.locGR_scoutTable)

    class Cliff(Jak1SubLevel):
        name = "Cliff"
        orb_count = 0

        def create_locations(self):
            self.create_cell_locations({k: Cells.locGR_cellTable[k] for k in {94}})

    def create_sub_levels(self):
        main = self.MainArea()
        cliff = self.Cliff()

        self.sub_levels[main.name] = main
        self.sub_levels[cliff.name] = cliff
