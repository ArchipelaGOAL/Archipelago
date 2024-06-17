from ..Regions import Jak1Level, Jak1SubLevel
from ..locs import (CellLocations as Cells,
                    ScoutLocations as Scouts,
                    SpecialLocations as Specials,
                    OrbCacheLocations as Caches)


class SentinelBeach(Jak1Level):
    name = "Sentinel Beach"
    total_orb_count = 150

    class MainArea(Jak1SubLevel):
        name = "Main Area"
        orb_count = 128

        def create_locations(self):
            self.create_cell_locations({k: Cells.locSB_cellTable[k] for k in {18, 21, 22}})
            self.create_fly_locations({k: Scouts.locSB_scoutTable[k] for k in {327700, 20, 65556, 262164, 393236}})
            self.create_cache_locations({k: Caches.loc_orbCacheTable[k] for k in {12634, 12635}})

    class Pelican(Jak1SubLevel):
        name = "Pelican"
        orb_count = 0

        def create_locations(self):
            self.create_cell_locations({k: Cells.locSB_cellTable[k] for k in {16}})

    class FlutFlutEgg(Jak1SubLevel):
        name = "Flut Flut Egg"
        orb_count = 0

        def create_locations(self):
            self.create_cell_locations({k: Cells.locSB_cellTable[k] for k in {17}})
            self.create_special_locations({k: Specials.loc_specialTable[k] for k in {17}})

    class EcoHarvesters(Jak1SubLevel):
        name = "Eco Harvesters"
        orb_count = 0

        def create_locations(self):
            self.create_cell_locations({k: Cells.locSB_cellTable[k] for k in {15}})

    class RidgeNearGreenVents(Jak1SubLevel):
        name = "Ridge Near Green Vents"
        orb_count = 5

        def create_locations(self):
            self.create_fly_locations({k: Scouts.locSB_scoutTable[k] for k in {131092}})

    class RidgeNearBlueVent(Jak1SubLevel):
        name = "Ridge Near Blue Vent"
        orb_count = 5

        def create_locations(self):
            self.create_fly_locations({k: Scouts.locSB_scoutTable[k] for k in {196628}})

    class CannonTower(Jak1SubLevel):
        name = "Cannon Tower"
        orb_count = 12

        def create_locations(self):
            self.create_cell_locations({k: Cells.locSB_cellTable[k] for k in {19}})

    def create_sub_levels(self):
        main = self.MainArea()
        pelican = self.Pelican()
        flut = self.FlutFlutEgg()
        harvesters = self.EcoHarvesters()
        green_ridge = self.RidgeNearGreenVents()
        blue_ridge = self.RidgeNearBlueVent()
        cannon = self.CannonTower()

        self.sub_levels[main.name] = main
        self.sub_levels[pelican.name] = pelican
        self.sub_levels[flut.name] = flut
        self.sub_levels[harvesters.name] = harvesters
        self.sub_levels[green_ridge.name] = green_ridge
        self.sub_levels[blue_ridge.name] = blue_ridge
        self.sub_levels[cannon.name] = cannon
