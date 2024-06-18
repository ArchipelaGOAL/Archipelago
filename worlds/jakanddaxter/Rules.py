import typing
from typing import List, Union
from BaseClasses import MultiWorld, CollectionState
from .JakAndDaxterOptions import JakAndDaxterOptions
from .locs import CellLocations as Cells
from .Locations import location_table
from .Regions import JakAndDaxterRegion


# TODO - Until we come up with a better progressive system for the traders (that avoids hard-locking if you pay the
#  wrong ones and can't afford the right ones) just make all the traders locked behind the total amount to pay them all.
def can_trade(multiworld: MultiWorld,
              player: int,
              region: JakAndDaxterRegion,
              traders: List[Union[List[int], int]],
              orb_count: int):

    def count_accessible_orbs(state) -> int:
        accessible_orbs = 0
        for reg in multiworld.get_regions(player):
            if reg.can_reach(state):
                accessible_orbs += typing.cast(JakAndDaxterRegion, reg).orb_count
        return accessible_orbs

    names_to_index = {region.locations[i].name: i for i in range(0, len(region.locations))}
    for trader in traders:

        # Singleton integers indicate a trader who has only one Location to check.
        # (Mayor, Uncle, etc)
        if type(trader) is int:
            loc = region.locations[names_to_index[location_table[Cells.to_ap_id(trader)]]]
            loc.access_rule = lambda state, orbs=orb_count: (
                    count_accessible_orbs(state) >= orbs)

        # Lists of integers indicate a trader who has sequential Locations to check, each dependent on the last.
        # (Oracles and Miners)
        elif type(trader) is list:
            previous_loc = None
            for trade in trader:
                loc = region.locations[names_to_index[location_table[Cells.to_ap_id(trade)]]]
                loc.access_rule = lambda state, orbs=orb_count, prev=previous_loc: (
                        count_accessible_orbs(state) >= orbs and
                        (state.can_reach(prev, player) if prev else True))  # TODO - Can Reach or Has Reached?
                previous_loc = loc

        # Any other type of element in the traders list is wrong.
        else:
            raise TypeError(f"Tried to set trade requirements on an unknown type {trader}.")


def can_free_scout_flies(state: CollectionState, player: int) -> bool:
    return (state.has("Crouch Uppercut", player)
            or state.has("Jump Dive", player))


def can_fight(state: CollectionState, player: int) -> bool:
    return (state.has("Jump Dive", player)
            or state.has("Jump Kick", player)
            or state.has("Punch", player)
            or state.has("Punch Uppercut", player)
            or state.has("Kick", player))
