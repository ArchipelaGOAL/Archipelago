from ..Regions import Jak1Level, Jak1SubLevel
from ..locs import (CellLocations as Cells,
                    ScoutLocations as Scouts,
                    SpecialLocations as Specials,
                    OrbCacheLocations as Caches)


class MistyIsland(Jak1Level):
    name = "Misty Island"
    total_orb_count = 150

    class MainArea(Jak1SubLevel):
        name = "Main Area"
        orb_count = 0

        def create_locations(self):
            pass

    class MuseCourse(Jak1SubLevel):
        name = "Muse Course"
        orb_count = 0

        def create_locations(self):
            self.create_cell_locations({k: Cells.locMI_cellTable[k] for k in {23}})
            self.create_fly_locations({k: Scouts.locMI_scoutTable[k] for k in {327708}})

    class Zoomer(Jak1SubLevel):
        name = "Zoomer"
        orb_count = 0

        def create_locations(self):
            self.create_cell_locations({k: Cells.locMI_cellTable[k] for k in {27, 29}})
            self.create_fly_locations({k: Scouts.locMI_scoutTable[k] for k in {393244}})

    class Ship(Jak1SubLevel):
        name = "Ship"
        orb_count = 0

        def create_locations(self):
            self.create_cell_locations({k: Cells.locMI_cellTable[k] for k in {24}})
            self.create_fly_locations({k: Scouts.locMI_scoutTable[k] for k in {131100}})

    class FarSide(Jak1SubLevel):
        name = "Far Side"
        orb_count = 0

        def create_locations(self):
            self.create_fly_locations({k: Scouts.locMI_scoutTable[k] for k in {28}})
            self.create_cache_locations({k: Caches.loc_orbCacheTable[k] for k in {11072}})

    class BarrelCourse(Jak1SubLevel):
        name = "Barrel Course"
        orb_count = 0

        def create_locations(self):
            self.create_cell_locations({k: Cells.locMI_cellTable[k] for k in {26}})
            self.create_fly_locations({k: Scouts.locMI_scoutTable[k] for k in {196636}})

    class UpperArenaApproach(Jak1SubLevel):
        name = "Upper Arena Approach"
        orb_count = 0

        def create_locations(self):
            self.create_fly_locations({k: Scouts.locMI_scoutTable[k] for k in {65564, 262172}})

    class LowerArenaApproach(Jak1SubLevel):
        name = "Lower Arena Approach"
        orb_count = 0

        def create_locations(self):
            self.create_cell_locations({k: Cells.locMI_cellTable[k] for k in {30}})

    class Arena(Jak1SubLevel):
        name = "Arena"
        orb_count = 0

        def create_locations(self):
            self.create_cell_locations({k: Cells.locMI_cellTable[k] for k in {25}})

    def create_sub_levels(self):
        main = self.MainArea()
        muse = self.MuseCourse()
        zoom = self.Zoomer()
        ship = self.Ship()
        far = self.FarSide()
        barrel = self.BarrelCourse()
        upper = self.UpperArenaApproach()
        lower = self.LowerArenaApproach()
        arena = self.Arena()

        self.sub_levels[main.name] = main
        self.sub_levels[muse.name] = muse
        self.sub_levels[zoom.name] = zoom
        self.sub_levels[ship.name] = ship
        self.sub_levels[far.name] = far
        self.sub_levels[barrel.name] = barrel
        self.sub_levels[upper.name] = upper
        self.sub_levels[lower.name] = lower
        self.sub_levels[arena.name] = arena
