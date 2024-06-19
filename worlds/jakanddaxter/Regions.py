import typing
from typing import Dict, Optional, Type

from BaseClasses import MultiWorld, Region, Location
from .Items import item_table
from .GameID import jak1_name
from .JakAndDaxterOptions import JakAndDaxterOptions
from .Locations import JakAndDaxterLocation, location_table
from .locs import (CellLocations as Cells,
                   ScoutLocations as Scouts,
                   SpecialLocations as Specials,
                   OrbCacheLocations as Caches)
from .regs import (GeyserRockRegions as GeyserRock,
                   SandoverVillageRegions as SandoverVillage,
                   ForbiddenJungleRegions as ForbiddenJungle,
                   SentinelBeachRegions as SentinelBeach,
                   MistyIslandRegions as MistyIsland,
                   FireCanyonRegions as FireCanyon,
                   RockVillageRegions as RockVillage,
                   PrecursorBasinRegions as PrecursorBasin,
                   LostPrecursorCityRegions as LostPrecursorCity,
                   BoggySwampRegions as BoggySwamp,
                   MountainPassRegions as MountainPass,
                   VolcanicCraterRegions as VolcanicCrater,
                   SpiderCaveRegions as SpiderCave,
                   SnowyMountainRegions as SnowyMountain,
                   LavaTubeRegions as LavaTube,
                   GolAndMaiasCitadelRegions as GolAndMaiasCitadel)


class JakAndDaxterRegion(Region):
    """
    Holds region information such as name, level name, number of orbs available, etc.
    We especially need orb counts to be tracked because we need to know when you can
    afford the 90-orb and 120-orb payments for more checks.
    """
    game: str = jak1_name
    level_name: str
    orb_count: int

    def __init__(self, name: str, player: int, multiworld: MultiWorld, level_name: str = None, orb_count: int = 0):
        formatted_name = f"{level_name} {name}".strip()
        super().__init__(formatted_name, player, multiworld)
        self.level_name = level_name
        self.orb_count = orb_count

    def add_cell_locations(self, locations: typing.List[int], access_rule=None):
        """
        Adds a Power Cell Location to this region with the given access rule.
        Converts Game ID's to AP ID's for you.
        """
        for loc in locations:
            self.add_jak_locations(Cells.to_ap_id(loc), access_rule)

    def add_fly_locations(self, locations: typing.List[int], access_rule=None):
        """
        Adds a Scout Fly Location to this region with the given access rule.
        Converts Game ID's to AP ID's for you.
        """
        for loc in locations:
            self.add_jak_locations(Scouts.to_ap_id(loc), access_rule)

    def add_special_locations(self, locations: typing.List[int], access_rule=None):
        """
        Adds a Special Location to this region with the given access rule.
        Converts Game ID's to AP ID's for you.
        Special Locations should be matched alongside their respective
        Power Cell Locations, so you get 2 unlocks for these rather than 1.
        """
        for loc in locations:
            self.add_jak_locations(Specials.to_ap_id(loc), access_rule)

    def add_cache_locations(self, locations: typing.List[int], access_rule=None):
        """
        Adds an Orb Cache Location to this region with the given access rule.
        Converts Game ID's to AP ID's for you.
        """
        for loc in locations:
            self.add_jak_locations(Caches.to_ap_id(loc), access_rule)

    def add_jak_locations(self, ap_id: int, access_rule=None):
        """
        Helper function to add Locations. Not to be used directly.
        """
        location = JakAndDaxterLocation(self.player, location_table[ap_id], ap_id, self)
        if access_rule:
            location.access_rule = access_rule
        self.locations.append(location)


def create_regions(multiworld: MultiWorld, options: JakAndDaxterOptions, player: int):

    # Always start with Menu.
    menu = JakAndDaxterRegion("Menu", player, multiworld)
    multiworld.regions.append(menu)

    # Build the special "Free 7 Scout Flies" Region. This is a virtual region always accessible to Menu.
    # The Power Cells within it are automatically checked when you receive the 7th scout fly for the corresponding cell.
    free7 = JakAndDaxterRegion("'Free 7 Scout Flies' Power Cells", player, multiworld)
    free7.add_cell_locations(Cells.loc7SF_cellTable.keys())
    for scout_fly_cell in free7.locations:

        # Translate from Cell AP ID to Scout AP ID using game ID as an intermediary.
        scout_fly_id = Scouts.to_ap_id(Cells.to_game_id(scout_fly_cell.address))
        scout_fly_cell.access_rule = lambda state, flies=scout_fly_id: state.has(item_table[flies], player, 7)

    # Build all regions. Include their intra-connecting Rules, their Locations, and their Location access rules.
    [gr] = GeyserRock.build_regions("Geyser Rock", player, multiworld)
    [sv] = SandoverVillage.build_regions("Sandover Village", player, multiworld)
    [fj] = ForbiddenJungle.build_regions("Forbidden Jungle", player, multiworld)
    [sb] = SentinelBeach.build_regions("Sentinel Beach", player, multiworld)
    [mi] = MistyIsland.build_regions("Misty Island", player, multiworld)
    [fc] = FireCanyon.build_regions("Fire Canyon", player, multiworld)
    [rv, rvc] = RockVillage.build_regions("Rock Village", player, multiworld)
    [pb] = PrecursorBasin.build_regions("Precursor Basin", player, multiworld)
    [lpc] = LostPrecursorCity.build_regions("Lost Precursor City", player, multiworld)
    [bs] = BoggySwamp.build_regions("Boggy Swamp", player, multiworld)
    [mp, mpr] = MountainPass.build_regions("Mountain Pass", player, multiworld)
    [vc] = VolcanicCrater.build_regions("Volcanic Crater", player, multiworld)
    [sc] = SpiderCave.build_regions("Spider Cave", player, multiworld)
    [sm] = SnowyMountain.build_regions("Snowy Mountain", player, multiworld)
    [lt] = LavaTube.build_regions("Lava Tube", player, multiworld)
    [gmc, fb] = GolAndMaiasCitadel.build_regions("Gol and Maia's Citadel", player, multiworld)

    # Define the interconnecting rules.
    menu.connect(free7)
    menu.connect(gr)
    gr.connect(sv)  # Geyser Rock modified to let you leave at any time.
    sv.connect(fj)
    sv.connect(sb)
    sv.connect(mi, rule=lambda state: state.has("Fisherman's Boat", player))
    sv.connect(fc, rule=lambda state: state.has("Power Cell", player, 20))
    fc.connect(rv)
    rv.connect(pb)
    rv.connect(lpc)
    rvc.connect(bs)  # rv->rvc connection defined internally by RockVillageRegions.
    rvc.connect(mp, rule=lambda state: state.has("Power Cell", player, 45))
    mpr.connect(vc)  # mp->mpr connection defined internally by MountainPassRegions.
    vc.connect(sc)
    vc.connect(sm, rule=lambda state: state.has("Snowy Mountain Gondola", player))
    vc.connect(lt, rule=lambda state: state.has("Power Cell", player, 72))
    lt.connect(gmc)  # gmc->fb connection defined internally by GolAndMaiasCitadelRegions.

    # Finally, set the completion condition.
    multiworld.completion_condition[player] = lambda state: state.can_reach(fb, "Region", player)

    # As a safety precaution, confirm that the total number of orbs in all regions is 2000.
    regs = [typing.cast(JakAndDaxterRegion, reg) for reg in multiworld.get_regions(player)]
    total_orbs = sum([reg.orb_count for reg in regs])
    assert total_orbs == 2000, f"The entire game has 2000 orbs, but we've only accounted for {total_orbs}!"
