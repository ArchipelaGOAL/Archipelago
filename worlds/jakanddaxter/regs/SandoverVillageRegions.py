from ..Regions import Jak1Level, Jak1SubLevel
from ..locs import (CellLocations as Cells,
                    ScoutLocations as Scouts,
                    OrbCacheLocations as Caches)


class SandoverVillage(Jak1Level):
    name = "Sandover Village"
    total_orb_count = 50

    class MainArea(Jak1SubLevel):
        name = "Main Area"
        orb_count = 26

        def create_locations(self):
            self.create_cell_locations({k: Cells.locSV_cellTable[k] for k in {11, 12, 10}})
            self.create_fly_locations({k: Scouts.locSV_scoutTable[k] for k in {262219, 327755, 131147, 65611, 196683}})

    class OrbCacheCliff(Jak1SubLevel):
        name = "Orb Cache Cliff"
        orb_count = 15

        def create_locations(self):
            self.create_cache_locations({k: Caches.loc_orbCacheTable[k] for k in {10344}})

    class YakowCliff(Jak1SubLevel):
        name = "Yakow Cliff"
        orb_count = 3

        def create_locations(self):
            self.create_fly_locations({k: Scouts.locSV_scoutTable[k] for k in {75}})

    class OraclePlatforms(Jak1SubLevel):
        name = "Oracle Platforms"
        orb_count = 6

        def create_locations(self):
            self.create_cell_locations({k: Cells.locSV_cellTable[k] for k in {13, 14}})
            self.create_fly_locations({k: Scouts.locSV_scoutTable[k] for k in {393291}})

    def create_sub_levels(self):
        main = self.MainArea()
        cache = self.OrbCacheCliff()
        yakow = self.YakowCliff()
        oracle = self.OraclePlatforms()

        self.sub_levels[main.name] = main
        self.sub_levels[cache.name] = cache
        self.sub_levels[yakow.name] = yakow
        self.sub_levels[oracle.name] = oracle
