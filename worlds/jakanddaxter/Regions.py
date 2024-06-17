import typing
from BaseClasses import MultiWorld, Region
from .GameID import jak1_name
from .JakAndDaxterOptions import JakAndDaxterOptions
from .Locations import JakAndDaxterLocation, location_table
from .Rules import Jak1Rule
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
    rules: typing.Dict[str, "Jak1Rule"]

    def __init__(self):
        self.create_sub_levels()
        assert len(self.sub_levels) > 0, f"Every Level must have at least one SubLevel, but {self.name} has none!"

        temp_total_orbs = sum(self.sub_levels[k].orb_count for k in self.sub_levels)
        assert self.total_orb_count == temp_total_orbs, \
            f"{self.name} should have {self.total_orb_count}, but its SubLevels only have {temp_total_orbs}!"

    def build_region(self, multiworld: MultiWorld, player: int):
        """
        Builds a Region object from this Level and adds it to the MultiWorld,
        iterating over all SubLevels and building Regions for them as well.
        """
        region = JakAndDaxterRegion(self.name, player, multiworld)
        for sub_level in self.sub_levels.values():
            sub_level.build_region(multiworld, player, self)

        for rule in sub_level.connecting_rules:
            region.connect()

        multiworld.regions.append(region)

    def create_sub_levels(self):
        """
        Create the list of SubLevels.
        """
        pass

    def create_rules(self, player: int):
        """
        Create the access rules from this Level to other Levels.
        """
        pass


class Jak1SubLevel:
    name: str
    orb_count: int
    locations: typing.Dict[int, str]
    location_rules: typing.Dict[int, "Jak1Rule"]
    connecting_rules: typing.Dict[str, "Jak1Rule"]

    def __init__(self):
        self.create_locations()
        assert len(self.locations) > 0, f"Every SubLevel must have at least one Location, but {self.name} has none!"

    def build_region(self, multiworld: MultiWorld, player: int, parent: Jak1Level):
        """
        Builds a Region object from this SubLevel and adds it to the MultiWorld,
        iterating over all Locations and building Locations (sic) for them as well.
        """
        formatted_name = f"{parent.name} {self.name}" if self.name else f"{parent.name}"
        region = JakAndDaxterRegion(formatted_name, player, multiworld)
        for loc in self.locations:

            location = JakAndDaxterLocation(player, self.locations[loc], loc, region)
            if self.location_rules[loc]:
                location.access_rule = self.location_rules[loc]

            region.locations.append(location)
        multiworld.regions.append(region)

    def create_locations(self):
        """
        Create the list of location checks.
        Use the original game ID's for each item to tell the Region which Locations are available in it.
        You do NOT need to add the item offsets or game ID, that will be handled by create_*_locations.
        """
        pass

    def create_location_rules(self, player: int):
        """
        Create the access rules for all the Locations within this SubLevel by ID.
        """
        pass

    def create_connecting_rules(self, player: int):
        """
        Create the access rules from this SubLevel to other SubLevels by Name.
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


def create_regions(multiworld: MultiWorld, options: JakAndDaxterOptions, player: int):

    # Always start with Menu.
    multiworld.regions.append(JakAndDaxterRegion("Menu", player, multiworld))

    # Go to town.
    for level in level_table.values():
        level.build_region(multiworld, player)
