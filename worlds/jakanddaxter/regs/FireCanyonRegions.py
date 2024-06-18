from typing import List
from BaseClasses import CollectionState, MultiWorld
from ..Regions import JakAndDaxterRegion
from ..Rules import can_free_scout_flies, can_trade, can_fight
from ..locs import CellLocations as Cells, ScoutLocations as Scouts


def build_regions(level_name: str, player: int, multiworld: MultiWorld) -> List[JakAndDaxterRegion]:

    main_area = JakAndDaxterRegion("Main Area", player, multiworld, level_name, 50)

    # Everything is accessible by making contact with the zoomer.
    main_area.add_cell_locations(Cells.locFC_cellTable.keys())
    main_area.add_fly_locations(Scouts.locFC_scoutTable.keys())

    return [main_area]
