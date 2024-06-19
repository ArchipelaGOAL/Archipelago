from typing import List
from BaseClasses import CollectionState, MultiWorld
from ..Regions import JakAndDaxterRegion
from ..Rules import can_free_scout_flies, can_trade, can_fight
from ..locs import CellLocations as Cells, ScoutLocations as Scouts


def build_regions(level_name: str, player: int, multiworld: MultiWorld) -> List[JakAndDaxterRegion]:

    # No area is inaccessible in VC even with only running and jumping.
    main_area = JakAndDaxterRegion("Main Area", player, multiworld, level_name, 50)

    # TODO - Figure out all the trade logic...
    main_area.add_cell_locations([96, 97, 98, 99, 100, 101], access_rule=lambda state:
                                 can_trade(multiworld, player, main_area, [96, 97, 98, 99, 100, 101], 1530))

    # Hidden Power Cell: you can carry yellow eco from Spider Cave just by running and jumping
    # and using your Goggles to shoot the box (you do not Punch to shoot from FP mode).
    main_area.add_cell_locations([74])

    # No blue eco sources in this area, all boxes must be broken by hand (yellow eco can't be carried far enough).
    main_area.add_fly_locations(Scouts.locVC_scoutTable.keys(), access_rule=lambda state:
                                can_free_scout_flies(state, player))

    return [main_area]
