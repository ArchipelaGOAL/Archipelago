from BaseClasses import CollectionState, MultiWorld
from ..Regions import JakAndDaxterRegion
from ..Rules import can_free_scout_flies, can_trade, can_fight
from ..locs import CellLocations as Cells, ScoutLocations as Scouts


def build_regions(level_name: str, player: int, multiworld: MultiWorld):

    fire_canyon = JakAndDaxterRegion("Fire Canyon", player, multiworld, level_name, 50)

    # Everything is accessible by making contact with the zoomer.
    fire_canyon.add_cell_locations(Cells.locFC_cellTable.keys())
    fire_canyon.add_fly_locations(Scouts.locFC_scoutTable.keys())
