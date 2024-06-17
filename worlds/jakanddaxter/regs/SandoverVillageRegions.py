from BaseClasses import CollectionState
from ..Regions import Jak1Level, Jak1SubLevel
from ..Rules import Jak1Rule
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
        main = SandoverVillage.MainArea()
        cache = SandoverVillage.OrbCacheCliff()
        yakow = SandoverVillage.YakowCliff()
        oracle = SandoverVillage.OraclePlatforms()

        self.sub_levels[main.name] = main
        self.sub_levels[cache.name] = cache
        self.sub_levels[yakow.name] = yakow
        self.sub_levels[oracle.name] = oracle

    def create_sub_rules(self, player: int):
        def main_cache(state: CollectionState) -> bool:
            return (state.has("Crouch Jump", player)
                    or state.has("Double Jump", player)
                    or (state.has("Crouch Uppercut", player)
                        and state.has("Jump Kick", player)))

        def main_yakow(state: CollectionState) -> bool:
            return (state.has("Crouch Jump", player)
                    or state.has("Double Jump", player)
                    or state.has("Crouch Uppercut", player))

        def main_oracle(state: CollectionState) -> bool:
            return (state.has("Roll Jump", player)
                    or (state.has("Double Jump", player)
                        and state.has("Jump Kick", player)))

        def farmers_scout_fly(state: CollectionState) -> bool:
            return (main_cache(state)
                    or Jak1Rule.can_break_scout_fly_box(state, player))

        self.sub_rules.append(Jak1Rule(self.sub_levels["Main Area"],
                                       self.sub_levels["Orb Cache Cliff"],
                                       main_cache))

        self.sub_rules.append(Jak1Rule(self.sub_levels["Orb Cache Cliff"],
                                       self.sub_levels["Main Area"]))

        self.sub_rules.append(Jak1Rule(self.sub_levels["Main Area"],
                                       Scouts.to_ap_id(196683),
                                       farmers_scout_fly))

        self.sub_rules.append(Jak1Rule(self.sub_levels["Main Area"],
                                       self.sub_levels["Yakow Cliff"],
                                       main_yakow))

        self.sub_rules.append(Jak1Rule(self.sub_levels["Yakow Cliff"],
                                       Scouts.to_ap_id(75),
                                       Jak1Rule.can_break_scout_fly_box))

        self.sub_rules.append(Jak1Rule(self.sub_levels["Yakow Cliff"],
                                       self.sub_levels["Main Area"]))

        self.sub_rules.append(Jak1Rule(self.sub_levels["Main Area"],
                                       self.sub_levels["Oracle Platforms"],
                                       main_oracle))

        self.sub_rules.append(Jak1Rule(self.sub_levels["Main Area"],
                                       Scouts.to_ap_id(393291),
                                       Jak1Rule.can_break_scout_fly_box))

        self.sub_rules.append(Jak1Rule(self.sub_levels["Oracle Platforms"],
                                       self.sub_levels["Main Area"]))

        # NOTES
        # - 5 Scout Flies in SV can be gotten with Blue Eco alone:
        #   - Sculptor, Bridge, Mayor, and Fisherman with eco from Sentinel Beach
        #   - Farmer with eco from Orb Cache Cliff, IF you can access it.
        # - The remaining 2 require a box-breaking move.
