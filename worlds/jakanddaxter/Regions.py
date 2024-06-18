import typing
from BaseClasses import MultiWorld, Region
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

    def __init__(self, name: str, player: int, multiworld: MultiWorld, level_name: str = "", orb_count: int = 0):
        formatted_name = f"{level_name} {name}" if name != level_name else name
        super().__init__(formatted_name, player, multiworld)
        self.level_name = level_name
        self.orb_count = orb_count

    def add_cell_locations(self, locations: typing.List[int], access_rule=None):
        """
        Helper function to add a Power Cell Location to this region with the given access rule.
        Converts Game ID's to AP ID's for you.
        """
        for loc in locations:
            ap_id = Cells.to_ap_id(loc)
            location = JakAndDaxterLocation(self.player, location_table[ap_id], ap_id, self)
            if access_rule:
                location.access_rule = access_rule
            self.locations.append(location)

    def add_fly_locations(self, locations: typing.List[int], access_rule=None):
        """
        Helper function to add a Power Cell Location to this region with the given access rule.
        Converts Game ID's to AP ID's for you.
        """
        for loc in locations:
            ap_id = Scouts.to_ap_id(loc)
            location = JakAndDaxterLocation(self.player, location_table[ap_id], ap_id, self)
            if access_rule:
                location.access_rule = access_rule
            self.locations.append(location)

    def add_special_locations(self, locations: typing.List[int], access_rule=None):
        """
        Helper function to add a Power Cell Location to this region with the given access rule.
        Converts Game ID's to AP ID's for you.
        Special Locations should be matched alongside their respective
        Power Cell Locations, so you get 2 unlocks for these rather than 1.
        """
        for loc in locations:
            ap_id = Specials.to_ap_id(loc)
            location = JakAndDaxterLocation(self.player, location_table[ap_id], ap_id, self)
            if access_rule:
                location.access_rule = access_rule
            self.locations.append(location)

    def add_cache_locations(self, locations: typing.List[int], access_rule=None):
        """
        Helper function to add a Power Cell Location to this region with the given access rule.
        Converts Game ID's to AP ID's for you.
        """
        for loc in locations:
            ap_id = Caches.to_ap_id(loc)
            location = JakAndDaxterLocation(self.player, location_table[ap_id], ap_id, self)
            if access_rule:
                location.access_rule = access_rule
            self.locations.append(location)


def create_regions(multiworld: MultiWorld, options: JakAndDaxterOptions, player: int):

    # Always start with Menu.
    multiworld.regions.append(JakAndDaxterRegion("Menu", player, multiworld))

    GeyserRock.build_regions("Geyser Rock", player, multiworld)
    SandoverVillage.build_regions("Sandover Village", player, multiworld)
    ForbiddenJungle.build_regions("Forbidden Jungle", player, multiworld)
    SentinelBeach.build_regions("Sentinel Beach", player, multiworld)
    MistyIsland.build_regions("Misty Island", player, multiworld)
    FireCanyon.build_regions("Fire Canyon", player, multiworld)
    RockVillage.build_regions("Rock Village", player, multiworld)
    PrecursorBasin.build_regions("Precursor Basin", player, multiworld)
    LostPrecursorCity.build_regions("Lost Precursor City", player, multiworld)
    BoggySwamp.build_regions("Boggy Swamp", player, multiworld)
    MountainPass.build_regions("Mountain Pass", player, multiworld)
    VolcanicCrater.build_regions("Volcanic Crater", player, multiworld)
    SpiderCave.build_regions("Spider Cave", player, multiworld)
    SnowyMountain.build_regions("Snowy Mountain", player, multiworld)
    LavaTube.build_regions("Lava Tube", player, multiworld)
    GolAndMaiasCitadel.build_regions("Gol and Maia's Citadel", player, multiworld)
