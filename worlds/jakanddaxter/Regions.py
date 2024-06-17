import typing
from BaseClasses import MultiWorld, Region
from .GameID import jak1_name
from .JakAndDaxterOptions import JakAndDaxterOptions
from .Locations import JakAndDaxterLocation, location_table
from .locs import (CellLocations as Cells,
                   ScoutLocations as Scouts,
                   SpecialLocations as Specials,
                   OrbCacheLocations as Caches)
from .regs import (ScoutFlyRegions as SF,
                   GeyserRockRegions as GR,
                   SandoverVillageRegions as SV,
                   SentinelBeachRegions as SB,
                   ForbiddenJungleRegions as FJ,
                   MistyIslandRegions as MI,
                   FireCanyonRegions as FC)


class JakAndDaxterRegion(Region):
    game: str = jak1_name


class Jak1Level:
    """
    Holds level information such as name, number of orbs available, etc.
    We especially need orb counts to be tracked because we need to know
    when you can afford the 90-orb and 120-orb payments for more checks.
    """
    name: str
    total_orb_count: int
    sub_levels: typing.Dict[str, "Jak1SubLevel"]
    sub_rules: typing.Dict[str, typing.Any]

    def __init__(self):
        self.create_sub_levels()
        assert len(self.sub_levels) > 0, f"Every Level must have at least one SubLevel, but {self.name} has none!"

        temp_total_orbs = sum(self.sub_levels[k].orb_count for k in self.sub_levels)
        assert self.total_orb_count == temp_total_orbs, \
            f"{self.name} should have {self.total_orb_count}, but its SubLevels only have {temp_total_orbs}!"

    def create_sub_levels(self):
        """
        Create the list of sublevels and fill them with location checks.
        """
        pass

    def create_access_rules(self):
        """
        Create the access rules for all the sublevels to/from each other.
        """
        pass


class Jak1SubLevel:
    name: str
    orb_count: int
    locations: typing.Dict[int, str]
    connecting_sub_levels: typing.Dict[str, "Jak1SubLevel"] = {}
    connecting_sub_rules: typing.Dict[str, typing.Any] = {}

    def __init__(self):
        self.create_locations()
        assert len(self.locations) > 0, f"Every SubLevel must have at least one Location, but {self.name} has none!"

    def create_locations(self):
        """
        Create the list of location checks.
        Use the original game ID's for each item to tell the Region which Locations are available in it.
        You do NOT need to add the item offsets or game ID, that will be handled by create_*_locations.
        """
        pass

    def create_cell_locations(self, locations: typing.Dict[int, str]):
        """
        Helper function to add a Power Cell in create_locations.
        Converts a Game ID to an AP ID.
        """
        self.locations = {**self.locations,
                          **{Cells.to_ap_id(loc): location_table[Cells.to_ap_id(loc)] for loc in locations}}

    def create_fly_locations(self, locations: typing.Dict[int, str]):
        """
        Helper function to add a Scout Fly in create_locations.
        Converts a Game ID to an AP ID.
        """
        self.locations = {**self.locations,
                          **{Scouts.to_ap_id(loc): location_table[Scouts.to_ap_id(loc)] for loc in locations}}

    def create_special_locations(self, locations: typing.Dict[int, str]):
        """
        Helper function to add a Special check in create_locations.
        Converts a Game ID to an AP ID.
        Special Locations should be matched alongside their respective
        Power Cell Locations, so you get 2 unlocks for these rather than 1.
        """
        self.locations = {**self.locations,
                          **{Specials.to_ap_id(loc): location_table[Specials.to_ap_id(loc)] for loc in locations}}

    def create_cache_locations(self, locations: typing.Dict[int, str]):
        """
        Helper function to add an Orb Cache in create_locations.
        Converts a Game ID to an AP ID.
        """
        self.locations = {**self.locations,
                          **{Caches.to_ap_id(loc): location_table[Caches.to_ap_id(loc)] for loc in locations}}


level_table: typing.Dict[str, Jak1Level] = {
    "Scout Fly Power Cells":  SF.ScoutFlyCells(),  # Virtual location.
    "Geyser Rock":            GR.GeyserRock(),
    "Sandover Village":       SV.SandoverVillage(),
    "Forbidden Jungle":       FJ.ForbiddenJungle(),
    "Sentinel Beach":         SB.SentinelBeach(),
    "Misty Island":           MI.MistyIsland(),
    "Fire Canyon":            FC.FireCanyon(),
    # "Rock Village":           Jak1Level("Rock Village", 50),
    # "Precursor Basin":        Jak1Level("Precursor Basin", 200),
    # "Lost Precursor City":    Jak1Level("Lost Precursor City", 200),
    # "Boggy Swamp":            Jak1Level("Boggy Swamp", 200),
    # "Mountain Pass":          Jak1Level("Mountain Pass", 50),
    # "Volcanic Crater":        Jak1Level("Volcanic Crater", 50),
    # "Spider Cave":            Jak1Level("Spider Cave", 200),
    # "Snowy Mountain":         Jak1Level("Snowy Mountain", 200),
    # "Lava Tube":              Jak1Level("Lava Tube", 50),
    # "Gol and Maia's Citadel": Jak1Level("Gol and Maia's Citadel", 200),
}

# TODO - Get rid of this.
sub_level_table: typing.Dict[str, Jak1SubLevel] = {
}


def create_regions(multiworld: MultiWorld, options: JakAndDaxterOptions, player: int):

    # Always start with Menu.
    multiworld.regions.append(JakAndDaxterRegion("Menu", player, multiworld))

    # Define each Region as a function of each of the SubLevels.
    for level in level_table.values():
        for sub_level in level.sub_levels.values():

            # Take the name from a combination of the Level name and SubLevel name.
            region = JakAndDaxterRegion(f"{level.name} {sub_level.name}", player, multiworld)
            for loc in sub_level.locations:

                # Take the Location name from the dictionary entry for `loc`,
                # and take the Location address as `loc` itself.
                location = JakAndDaxterLocation(player, sub_level.locations[loc], loc, region)
                region.locations += location

            # Once all Locations are added to the Region, add the Region to the Multiworld.
            multiworld.regions.append(region)


#     region_rv = create_region(player, multiworld, Jak1Level.ROCK_VILLAGE)
#     create_cell_locations(region_rv, Cells.locRV_cellTable)
#     create_fly_locations(region_rv, {k: Scouts.locRV_scoutTable[k]
#                                      for k in {76, 131148, 196684, 262220, 65612, 327756}})
#     create_special_locations(region_rv, {k: Specials.loc_specialTable[k] for k in {33}})
#
#     sub_region_rvpb = create_subregion(region_rv, Jak1SubLevel.ROCK_VILLAGE_PONTOON_BRIDGE)
#     create_fly_locations(sub_region_rvpb, {k: Scouts.locRV_scoutTable[k] for k in {393292}})
#
#     region_pb = create_region(player, multiworld, Jak1Level.PRECURSOR_BASIN)
#     create_cell_locations(region_pb, Cells.locPB_cellTable)
#     create_fly_locations(region_pb, Scouts.locPB_scoutTable)
#
#     region_lpc = create_region(player, multiworld, Jak1Level.LOST_PRECURSOR_CITY)
#     create_cell_locations(region_lpc, Cells.locLPC_cellTable)
#     create_fly_locations(region_lpc, Scouts.locLPC_scoutTable)
#
#     region_bs = create_region(player, multiworld, Jak1Level.BOGGY_SWAMP)
#     create_cell_locations(region_bs, {k: Cells.locBS_cellTable[k] for k in {36, 38, 39, 40, 41, 42}})
#     create_fly_locations(region_bs, {k: Scouts.locBS_scoutTable[k] for k in {43, 393259, 65579, 262187, 196651}})
#
#     sub_region_bsff = create_subregion(region_bs, Jak1SubLevel.BOGGY_SWAMP_FLUT_FLUT)
#     create_cell_locations(sub_region_bsff, {k: Cells.locBS_cellTable[k] for k in {37}})
#     create_fly_locations(sub_region_bsff, {k: Scouts.locBS_scoutTable[k] for k in {327723, 131115}})
#
#     region_mp = create_region(player, multiworld, Jak1Level.MOUNTAIN_PASS)
#     create_cell_locations(region_mp, {k: Cells.locMP_cellTable[k] for k in {86, 87}})
#     create_fly_locations(region_mp, Scouts.locMP_scoutTable)
#
#     sub_region_mps = create_subregion(region_mp, Jak1SubLevel.MOUNTAIN_PASS_SHORTCUT)
#     create_cell_locations(sub_region_mps, {k: Cells.locMP_cellTable[k] for k in {110}})
#
#     region_vc = create_region(player, multiworld, Jak1Level.VOLCANIC_CRATER)
#     create_cell_locations(region_vc, Cells.locVC_cellTable)
#     create_fly_locations(region_vc, Scouts.locVC_scoutTable)
#     create_special_locations(region_vc, {k: Specials.loc_specialTable[k] for k in {105}})
#
#     region_sc = create_region(player, multiworld, Jak1Level.SPIDER_CAVE)
#     create_cell_locations(region_sc, Cells.locSC_cellTable)
#     create_fly_locations(region_sc, Scouts.locSC_scoutTable)
#
#     region_sm = create_region(player, multiworld, Jak1Level.SNOWY_MOUNTAIN)
#     create_cell_locations(region_sm, {k: Cells.locSM_cellTable[k] for k in {60, 61, 66, 64}})
#     create_fly_locations(region_sm, {k: Scouts.locSM_scoutTable[k] for k in {65, 327745, 65601, 131137, 393281}})
#     create_special_locations(region_sm, {k: Specials.loc_specialTable[k] for k in {60}})
#
#     sub_region_smfb = create_subregion(region_sm, Jak1SubLevel.SNOWY_MOUNTAIN_FROZEN_BOX)
#     create_cell_locations(sub_region_smfb, {k: Cells.locSM_cellTable[k] for k in {67}})
#
#     sub_region_smff = create_subregion(region_sm, Jak1SubLevel.SNOWY_MOUNTAIN_FLUT_FLUT)
#     create_cell_locations(sub_region_smff, {k: Cells.locSM_cellTable[k] for k in {63}})
#     create_special_locations(sub_region_smff, {k: Specials.loc_specialTable[k] for k in {63}})
#
#     sub_region_smlf = create_subregion(region_sm, Jak1SubLevel.SNOWY_MOUNTAIN_LURKER_FORT)
#     create_cell_locations(sub_region_smlf, {k: Cells.locSM_cellTable[k] for k in {62}})
#     create_fly_locations(sub_region_smlf, {k: Scouts.locSM_scoutTable[k] for k in {196673, 262209}})
#
#     region_lt = create_region(player, multiworld, Jak1Level.LAVA_TUBE)
#     create_cell_locations(region_lt, Cells.locLT_cellTable)
#     create_fly_locations(region_lt, Scouts.locLT_scoutTable)
#
#     region_gmc = create_region(player, multiworld, Jak1Level.GOL_AND_MAIAS_CITADEL)
#     create_cell_locations(region_gmc, {k: Cells.locGMC_cellTable[k] for k in {71, 72, 73}})
#     create_fly_locations(region_gmc, {k: Scouts.locGMC_scoutTable[k]
#                                       for k in {91, 65627, 196699, 262235, 393307, 131163}})
#     create_special_locations(region_gmc, {k: Specials.loc_specialTable[k] for k in {71, 72, 73}})
#
#     sub_region_gmcrt = create_subregion(region_gmc, Jak1SubLevel.GOL_AND_MAIAS_CITADEL_ROTATING_TOWER)
#     create_cell_locations(sub_region_gmcrt, {k: Cells.locGMC_cellTable[k] for k in {70}})
#     create_fly_locations(sub_region_gmcrt, {k: Scouts.locGMC_scoutTable[k] for k in {327771}})
#     create_special_locations(sub_region_gmcrt, {k: Specials.loc_specialTable[k] for k in {70}})
#
#     create_subregion(sub_region_gmcrt, Jak1SubLevel.GOL_AND_MAIAS_CITADEL_FINAL_BOSS)
#
#
# def create_region(player: int, multiworld: MultiWorld, level: Jak1Level) -> JakAndDaxterRegion:
#     name = level_table[level].name
#     region = JakAndDaxterRegion(name, player, multiworld)
#     multiworld.regions.append(region)
#     return region
#
#
# def create_subregion(parent: Region, sub_level: Jak1SubLevel) -> JakAndDaxterRegion:
#     name = sub_level_table[sub_level].name
#     region = JakAndDaxterRegion(name, parent.player, parent.multiworld)
#     parent.multiworld.regions.append(region)
#     return region
