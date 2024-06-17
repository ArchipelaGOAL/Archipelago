from ..Regions import Jak1Level, Jak1SubLevel
from ..locs import (CellLocations as Cells,
                    ScoutLocations as Scouts,
                    SpecialLocations as Specials,
                    OrbCacheLocations as Caches)


class ForbiddenJungle(Jak1Level):
    name = "Forbidden Jungle"
    total_orb_count = 150

    class MainArea(Jak1SubLevel):
        name = "Main Area"
        orb_count = 25

        def create_locations(self):
            self.create_fly_locations({k: Scouts.locFJ_scoutTable[k] for k in {393223}})

    class LurkerMachine(Jak1SubLevel):
        name = "Lurker Machine"
        orb_count = 5

        def create_locations(self):
            self.create_cell_locations({k: Cells.locFJ_cellTable[k] for k in {3, 9}})
            self.create_fly_locations({k: Scouts.locFJ_scoutTable[k] for k in {131079}})

    class River(Jak1SubLevel):
        name = "River"
        orb_count = 42

        def create_locations(self):
            self.create_cell_locations({k: Cells.locFJ_cellTable[k] for k in {5, 8}})
            self.create_fly_locations({k: Scouts.locFJ_scoutTable[k] for k in {7, 196615}})
            self.create_special_locations({k: Specials.loc_specialTable[k] for k in {5}})
            self.create_cache_locations({k: Caches.loc_orbCacheTable[k] for k in {10369}})

    class TempleExit(Jak1SubLevel):
        name = "Temple Exit"
        orb_count = 12

        def create_locations(self):
            self.create_fly_locations({k: Scouts.locFJ_scoutTable[k] for k in {262151}})

    class TempleExterior(Jak1SubLevel):
        name = "Temple Exterior"
        orb_count = 10

        def create_locations(self):
            self.create_cell_locations({k: Cells.locFJ_cellTable[k] for k in {4}})
            self.create_fly_locations({k: Scouts.locFJ_scoutTable[k] for k in {327687, 65543}})
            self.create_special_locations({k: Specials.loc_specialTable[k] for k in {4}})

    class TempleInteriorPreBlueEco(Jak1SubLevel):
        name = "Temple Interior (Pre Blue Eco)"
        orb_count = 17

        def create_locations(self):
            self.create_cell_locations({k: Cells.locFJ_cellTable[k] for k in {2}})
            self.create_special_locations({k: Specials.loc_specialTable[k] for k in {2}})

    class TempleInteriorPostBlueEco(Jak1SubLevel):
        name = "Temple Interior (Post Blue Eco)"
        orb_count = 39

        def create_locations(self):
            self.create_cell_locations({k: Cells.locFJ_cellTable[k] for k in {6}})

    def create_sub_levels(self):
        main = self.MainArea()
        machine = self.LurkerMachine()
        river = self.River()
        t_exit = self.TempleExit()
        t_exterior = self.TempleExterior()
        t_interior_pre = self.TempleInteriorPreBlueEco()
        t_interior_post = self.TempleInteriorPostBlueEco()

        self.sub_levels[main.name] = main
        self.sub_levels[machine.name] = machine
        self.sub_levels[river.name] = river
        self.sub_levels[t_exit.name] = t_exit
        self.sub_levels[t_exterior.name] = t_exterior
        self.sub_levels[t_interior_pre.name] = t_interior_pre
        self.sub_levels[t_interior_post.name] = t_interior_post
