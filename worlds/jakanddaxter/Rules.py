from typing import List

from BaseClasses import MultiWorld, CollectionState
from .JakAndDaxterOptions import JakAndDaxterOptions
from .Regions import Jak1Level, Jak1SubLevel, level_table, sub_level_table
from .Items import item_table
from .locs import CellLocations as Cells, ScoutLocations as Scouts, SpecialLocations as Specials


def set_rules(multiworld: MultiWorld, options: JakAndDaxterOptions, player: int):

    # Setting up some useful variables here because the offset numbers can get confusing
    # for access rules. Feel free to add more variables here to keep the code more readable.
    # You DO need to convert the game ID's to AP ID's here.
    power_cell = item_table[Cells.to_ap_id(0)]

    sv_traders = [item_table[Specials.to_ap_id(k)] for k in {11, 12, 13, 14}]
    rv_traders = [item_table[Specials.to_ap_id(k)] for k in {31, 32, 33, 34, 35}]
    vc_traders = [item_table[Specials.to_ap_id(k)] for k in {96, 97, 98, 99, 100, 101}]

    fj_jungle_elevator = item_table[Specials.to_ap_id(4)]
    fj_blue_switch = item_table[Specials.to_ap_id(2)]
    fj_fisherman = item_table[Specials.to_ap_id(5)]

    sb_flut_flut = item_table[Specials.to_ap_id(17)]
    sm_yellow_switch = item_table[Specials.to_ap_id(60)]
    sm_fort_gate = item_table[Specials.to_ap_id(63)]

    gmc_blue_sage = item_table[Specials.to_ap_id(71)]
    gmc_red_sage = item_table[Specials.to_ap_id(72)]
    gmc_yellow_sage = item_table[Specials.to_ap_id(73)]
    gmc_green_sage = item_table[Specials.to_ap_id(70)]

    # Start connecting regions and set their access rules.

    # Scout Fly Power Cells is a virtual region, not a physical one, so connect it to Menu.
    connect_start(multiworld, player, Jak1Level.SCOUT_FLY_POWER_CELLS)
    set_fly_requirements(multiworld, player)

    # You start the game in front of Green Sage's Hut, so you don't get stuck on Geyser Rock in the first 5 minutes.
    connect_start(multiworld, player, Jak1Level.SANDOVER_VILLAGE)
    set_trade_requirements(multiworld, player, Jak1Level.SANDOVER_VILLAGE, sv_traders, 1530)

    # Geyser Rock is accessible at any time, just check the 3 naked cell Locations to return.
    connect_regions(multiworld, player,
                    Jak1Level.SANDOVER_VILLAGE,
                    Jak1Level.GEYSER_ROCK)

    connect_regions(multiworld, player,
                    Jak1Level.SANDOVER_VILLAGE,
                    Jak1Level.FORBIDDEN_JUNGLE)

    connect_region_to_sub(multiworld, player,
                          Jak1Level.FORBIDDEN_JUNGLE,
                          Jak1SubLevel.FORBIDDEN_JUNGLE_SWITCH_ROOM,
                          lambda state: state.has(fj_jungle_elevator, player))

    connect_subregions(multiworld, player,
                       Jak1SubLevel.FORBIDDEN_JUNGLE_SWITCH_ROOM,
                       Jak1SubLevel.FORBIDDEN_JUNGLE_PLANT_ROOM,
                       lambda state: state.has(fj_blue_switch, player))

    # You just need to defeat the plant boss to escape this subregion, no specific Item required.
    connect_sub_to_region(multiworld, player,
                          Jak1SubLevel.FORBIDDEN_JUNGLE_PLANT_ROOM,
                          Jak1Level.FORBIDDEN_JUNGLE)

    connect_regions(multiworld, player,
                    Jak1Level.SANDOVER_VILLAGE,
                    Jak1Level.SENTINEL_BEACH)

    # Just jump off the tower to escape this subregion.
    connect_region_to_sub(multiworld, player,
                          Jak1Level.SENTINEL_BEACH,
                          Jak1SubLevel.SENTINEL_BEACH_CANNON_TOWER,
                          lambda state: state.has(fj_blue_switch, player))

    connect_regions(multiworld, player,
                    Jak1Level.SANDOVER_VILLAGE,
                    Jak1Level.MISTY_ISLAND,
                    lambda state: state.has(fj_fisherman, player))

    connect_regions(multiworld, player,
                    Jak1Level.SANDOVER_VILLAGE,
                    Jak1Level.FIRE_CANYON,
                    lambda state: state.has(power_cell, player, 20))

    connect_regions(multiworld, player,
                    Jak1Level.FIRE_CANYON,
                    Jak1Level.ROCK_VILLAGE)
    set_trade_requirements(multiworld, player, Jak1Level.ROCK_VILLAGE, rv_traders, 1530)

    connect_regions(multiworld, player,
                    Jak1Level.ROCK_VILLAGE,
                    Jak1Level.PRECURSOR_BASIN)

    # This is another virtual location that shares it's "borders" with its parent location.
    # You can do blue rings as soon as you finish purple rings.
    connect_region_to_sub(multiworld, player,
                          Jak1Level.PRECURSOR_BASIN,
                          Jak1SubLevel.PRECURSOR_BASIN_BLUE_RINGS)

    connect_regions(multiworld, player,
                    Jak1Level.ROCK_VILLAGE,
                    Jak1Level.LOST_PRECURSOR_CITY)

    connect_region_to_sub(multiworld, player,
                          Jak1Level.LOST_PRECURSOR_CITY,
                          Jak1SubLevel.LOST_PRECURSOR_CITY_SUNKEN_ROOM)

    connect_subregions(multiworld, player,
                       Jak1SubLevel.LOST_PRECURSOR_CITY_SUNKEN_ROOM,
                       Jak1SubLevel.LOST_PRECURSOR_CITY_HELIX_ROOM)

    # LPC is such a mess logistically... once you complete the climb up the helix room,
    # you are back to the room before the first slide, which is still the "main area" of LPC.
    connect_sub_to_region(multiworld, player,
                          Jak1SubLevel.LOST_PRECURSOR_CITY_HELIX_ROOM,
                          Jak1Level.LOST_PRECURSOR_CITY)

    # Once you raise the sunken room to the surface, you can access Rock Village directly.
    # You just need to complete the Location check to do this, you don't need to receive the power cell Item.
    connect_sub_to_region(multiworld, player,
                          Jak1SubLevel.LOST_PRECURSOR_CITY_SUNKEN_ROOM,
                          Jak1Level.ROCK_VILLAGE)

    connect_regions(multiworld, player,
                    Jak1Level.ROCK_VILLAGE,
                    Jak1Level.BOGGY_SWAMP)

    # Flut Flut only has one landing pad here, so leaving this subregion is as easy
    # as dismounting Flut Flut right where you found her.
    connect_region_to_sub(multiworld, player,
                          Jak1Level.BOGGY_SWAMP,
                          Jak1SubLevel.BOGGY_SWAMP_FLUT_FLUT,
                          lambda state: state.has(sb_flut_flut, player))

    # Klaww is considered the "main area" of MP, and the "race" is a subregion.
    # It's not really intended to get back up the ledge overlooking Klaww's lava pit.
    connect_regions(multiworld, player,
                    Jak1Level.ROCK_VILLAGE,
                    Jak1Level.MOUNTAIN_PASS,
                    lambda state: state.has(power_cell, player, 45))

    connect_region_to_sub(multiworld, player,
                          Jak1Level.MOUNTAIN_PASS,
                          Jak1SubLevel.MOUNTAIN_PASS_RACE)

    connect_subregions(multiworld, player,
                       Jak1SubLevel.MOUNTAIN_PASS_RACE,
                       Jak1SubLevel.MOUNTAIN_PASS_SHORTCUT,
                       lambda state: state.has(sm_yellow_switch, player))

    connect_sub_to_region(multiworld, player,
                          Jak1SubLevel.MOUNTAIN_PASS_RACE,
                          Jak1Level.VOLCANIC_CRATER)
    set_trade_requirements(multiworld, player, Jak1Level.VOLCANIC_CRATER, vc_traders, 1530)

    connect_regions(multiworld, player,
                    Jak1Level.VOLCANIC_CRATER,
                    Jak1Level.SPIDER_CAVE)

    # TODO - Yeah, this is a weird one. You technically need either 71 power cells OR
    #  any 2 power cells after arriving at Volcanic Crater. Not sure how to model this...
    connect_regions(multiworld, player,
                    Jak1Level.VOLCANIC_CRATER,
                    Jak1Level.SNOWY_MOUNTAIN)

    connect_region_to_sub(multiworld, player,
                          Jak1Level.SNOWY_MOUNTAIN,
                          Jak1SubLevel.SNOWY_MOUNTAIN_FROZEN_BOX,
                          lambda state: state.has(sm_yellow_switch, player))

    # Flut Flut has both a start and end landing pad here, but there's an elevator that takes you up
    # from the end pad to the entrance of the fort, so you're back to the "main area."
    connect_region_to_sub(multiworld, player,
                          Jak1Level.SNOWY_MOUNTAIN,
                          Jak1SubLevel.SNOWY_MOUNTAIN_FLUT_FLUT,
                          lambda state: state.has(sb_flut_flut, player))

    connect_region_to_sub(multiworld, player,
                          Jak1Level.SNOWY_MOUNTAIN,
                          Jak1SubLevel.SNOWY_MOUNTAIN_LURKER_FORT,
                          lambda state: state.has(sm_fort_gate, player))

    connect_regions(multiworld, player,
                    Jak1Level.VOLCANIC_CRATER,
                    Jak1Level.LAVA_TUBE,
                    lambda state: state.has(power_cell, player, 72))

    connect_regions(multiworld, player,
                    Jak1Level.LAVA_TUBE,
                    Jak1Level.GOL_AND_MAIAS_CITADEL)

    # The stairs up to Samos's cage is only activated when you get the Items for freeing the other 3 Sages.
    # But you can climb back down that staircase (or fall down from the top) to escape this subregion.
    connect_region_to_sub(multiworld, player,
                          Jak1Level.GOL_AND_MAIAS_CITADEL,
                          Jak1SubLevel.GOL_AND_MAIAS_CITADEL_ROTATING_TOWER,
                          lambda state: state.has(gmc_blue_sage) and
                                        state.has(gmc_red_sage) and
                                        state.has(gmc_yellow_sage))

    # This is the final elevator, only active when you get the Item for freeing the Green Sage.
    connect_subregions(multiworld, player,
                       Jak1SubLevel.GOL_AND_MAIAS_CITADEL_ROTATING_TOWER,
                       Jak1SubLevel.GOL_AND_MAIAS_CITADEL_FINAL_BOSS,
                       lambda state: state.has(gmc_green_sage, player))

    multiworld.completion_condition[player] = lambda state: state.can_reach(
        multiworld.get_region(sub_level_table[Jak1SubLevel.GOL_AND_MAIAS_CITADEL_FINAL_BOSS].name, player),
        "Region",
        player)


def connect_start(multiworld: MultiWorld, player: int, target: Jak1Level):
    menu_region = multiworld.get_region("Menu", player)
    start_region = multiworld.get_region(level_table[target].name, player)
    menu_region.connect(start_region)


def connect_regions(multiworld: MultiWorld, player: int, source: Jak1Level, target: Jak1Level, rule=None):
    source_region = multiworld.get_region(level_table[source].name, player)
    target_region = multiworld.get_region(level_table[target].name, player)
    source_region.connect(target_region, rule=rule)


def connect_region_to_sub(multiworld: MultiWorld, player: int, source: Jak1Level, target: Jak1SubLevel, rule=None):
    source_region = multiworld.get_region(level_table[source].name, player)
    target_region = multiworld.get_region(sub_level_table[target].name, player)
    source_region.connect(target_region, rule=rule)


def connect_sub_to_region(multiworld: MultiWorld, player: int, source: Jak1SubLevel, target: Jak1Level, rule=None):
    source_region = multiworld.get_region(sub_level_table[source].name, player)
    target_region = multiworld.get_region(level_table[target].name, player)
    source_region.connect(target_region, rule=rule)


def connect_subregions(multiworld: MultiWorld, player: int, source: Jak1SubLevel, target: Jak1SubLevel, rule=None):
    source_region = multiworld.get_region(sub_level_table[source].name, player)
    target_region = multiworld.get_region(sub_level_table[target].name, player)
    source_region.connect(target_region, rule=rule)


# The "Free 7 Scout Fly" Locations are automatically checked when you receive the 7th scout fly Item.
def set_fly_requirements(multiworld: MultiWorld, player: int):
    region = multiworld.get_region(level_table[Jak1Level.SCOUT_FLY_POWER_CELLS].name, player)
    for loc in region.locations:
        scout_fly_id = Scouts.to_ap_id(Cells.to_game_id(loc.address))  # Translate using game ID as an intermediary.
        loc.access_rule = lambda state, flies=scout_fly_id: state.has(item_table[flies], player, 7)


# TODO - Until we come up with a better progressive system for the traders (that avoids hard-locking if you pay the
#  wrong ones and can't afford the right ones) just make all the traders locked behind the total amount to pay them all.
def set_trade_requirements(multiworld: MultiWorld, player: int, level: Jak1Level, traders: List[int], orb_count: int):

    def count_accessible_orbs(state) -> int:
        accessible_orbs = 0
        for level_info in [*level_table.values(), *sub_level_table.values()]:
            reg = multiworld.get_region(level_info.name, player)
            if reg.can_reach(state):
                accessible_orbs += level_info.orb_count
        return accessible_orbs

    region = multiworld.get_region(level_table[level].name, player)
    for loc in region.locations:
        if loc in traders:
            loc.access_rule = lambda state, orbs=orb_count: count_accessible_orbs(state) >= orbs
