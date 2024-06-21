from typing import List
from BaseClasses import CollectionState, MultiWorld
from .RegionBase import JakAndDaxterRegion
from ..locs import ScoutLocations as Scouts


def build_regions(level_name: str, player: int, multiworld: MultiWorld) -> List[JakAndDaxterRegion]:

    main_area = JakAndDaxterRegion(f"{level_name} Main Area", player, multiworld, level_name, 50)
    main_area.add_cell_locations([92, 93])
    main_area.add_fly_locations(Scouts.locGR_scoutTable.keys())  # All Flies here are accessible with blue eco.

    cliff = JakAndDaxterRegion(f"{level_name} Cliff", player, multiworld, level_name, 0)
    cliff.add_cell_locations([94])

    main_area.connect(cliff, rule=lambda state: (state.has("Crouch Jump", player)
                                                 or state.has("Crouch Uppercut", player)
                                                 or state.has("Double Jump", player)))

    multiworld.regions.append(main_area)
    multiworld.regions.append(cliff)

    return [main_area]
