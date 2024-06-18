from typing import List
from BaseClasses import CollectionState, MultiWorld
from ..Regions import JakAndDaxterRegion
from ..Rules import can_free_scout_flies, can_trade, can_fight


# TODO - Map out Precursor Orbs on Misty Island!!!
def build_regions(level_name: str, player: int, multiworld: MultiWorld) -> List[JakAndDaxterRegion]:
    
    main_area = JakAndDaxterRegion("Main Area", player, multiworld, level_name, 0)

    muse_course = JakAndDaxterRegion("Muse Course", player, multiworld, level_name, 0)
    muse_course.add_cell_locations([23])
    muse_course.add_fly_locations([327708], access_rule=lambda state: can_free_scout_flies(state, player))

    zoomer = JakAndDaxterRegion("Zoomer", player, multiworld, level_name, 0)

    # Just hit these things with the zoomer.
    zoomer.add_cell_locations([27, 29])
    zoomer.add_fly_locations([393244])

    ship = JakAndDaxterRegion("Ship", player, multiworld, level_name, 0)
    ship.add_cell_locations([24])
    ship.add_fly_locations([131100], access_rule=lambda state: can_free_scout_flies(state, player))

    far_side = JakAndDaxterRegion("Far Side", player, multiworld, level_name, 0)

    # In order to even reach this fly, you must use the seesaw, which requires Jump Dive.
    far_side.add_fly_locations([28], access_rule=lambda state: state.has("Jump Dive", player))

    # To carry the blue eco fast enough to open this cache, you need to break the bone bridges along the way.
    far_side.add_cache_locations([11072], access_rule=lambda state: can_fight(state, player))

    barrel_course = JakAndDaxterRegion("Barrel Course", player, multiworld, level_name, 0)
    barrel_course.add_cell_locations([26], access_rule=lambda state: can_fight(state, player))
    barrel_course.add_fly_locations([196636], access_rule=lambda state: can_free_scout_flies(state, player))

    upper_approach = JakAndDaxterRegion("Upper Arena Approach", player, multiworld, level_name, 0)
    upper_approach.add_fly_locations([65564, 262172], access_rule=lambda state:
                                     can_free_scout_flies(state, player))

    lower_approach = JakAndDaxterRegion("Lower Arena Approach", player, multiworld, level_name, 0)
    lower_approach.add_cell_locations([30])

    arena = JakAndDaxterRegion("Arena", player, multiworld, level_name, 0)
    arena.add_cell_locations([25], access_rule=lambda state: can_fight(state, player))

    main_area.connect(muse_course)             # TODO - What do you need to chase the muse the whole way around?
    main_area.connect(zoomer)                  # Run and jump down.
    main_area.connect(ship)                    # Run and jump.
    main_area.connect(lower_approach)          # Run and jump.

    # Need to break the bone bridge to access.
    main_area.connect(upper_approach, rule=lambda state: can_fight(state, player))

    muse_course.connect(main_area)             # Run and jump down.

    # The zoomer pad is low enough that it requires Crouch Jump specifically.
    zoomer.connect(main_area, rule=lambda state: state.has("Crouch Jump", player))

    ship.connect(main_area)                    # Run and jump down.
    ship.connect(far_side)                     # Run.
    ship.connect(barrel_course)                # Run and jump (dodge barrels).

    # No connections from far_side to arena because arena is locked from the back until you beat the ambush.
    far_side.connect(ship)                     # Run (dodge enemies?).

    barrel_course.connect(arena)               # Jump down.

    upper_approach.connect(lower_approach)     # Jump down.
    upper_approach.connect(arena)              # Jump down.

    lower_approach.connect(upper_approach)     # TODO - Do you need a way to gain height?

    # Requires breaking bone bridges.
    lower_approach.connect(arena, rule=lambda state: can_fight(state, player))

    arena.connect(lower_approach)              # Run.
    arena.connect(far_side)                    # Run.

    multiworld.regions.append(main_area)
    multiworld.regions.append(muse_course)
    multiworld.regions.append(zoomer)
    multiworld.regions.append(ship)
    multiworld.regions.append(far_side)
    multiworld.regions.append(barrel_course)
    multiworld.regions.append(upper_approach)
    multiworld.regions.append(lower_approach)
    multiworld.regions.append(arena)

    return [main_area]
