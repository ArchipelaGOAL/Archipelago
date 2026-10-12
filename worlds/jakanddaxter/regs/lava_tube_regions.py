from .region_base import JakAndDaxterRegion
from ..options import EnableOrbsanity
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import JakAndDaxterWorld
from ..rules import can_reach_orbs_level
from ..locs import cell_locations as cells, scout_locations as scouts


def build_regions(level_name: str, world: "JakAndDaxterWorld") -> tuple[JakAndDaxterRegion, ...]:
    multiworld = world.multiworld
    options = world.options
    player = world.player

    main_area = JakAndDaxterRegion("Main Area", player, multiworld, level_name, 50)
    main_area.add_fly_locations([90, 65626])

    behind_oranges_door = JakAndDaxterRegion("Behind Oranges Door", player, multiworld, level_name, 0)
    behind_oranges_door.add_cell_locations(cells.locLT_cellTable.keys())
    behind_oranges_door.add_fly_locations([327770, 262234, 131162, 196698, 393306])

    if options.lava_tube_oranges_skip:
        # It's possible to glitch through/around the door in the room with the "oranges", requiring no yellow eco.
        main_area.connect(behind_oranges_door)
    else:
        main_area.connect(behind_oranges_door, rule=lambda state: state.has("Yellow Eco", player))

    world.level_to_regions[level_name].append(main_area)
    world.level_to_regions[level_name].append(behind_oranges_door)

    # If Per-Level Orbsanity is enabled, build the special Orbsanity Region. This is a virtual region always
    # accessible to Main Area. The Locations within are automatically checked when you collect enough orbs.
    if options.enable_orbsanity == EnableOrbsanity.option_per_level:
        orbs = JakAndDaxterRegion("Orbsanity", player, multiworld, level_name)

        bundle_count = 50 // world.orb_bundle_size
        for bundle_index in range(bundle_count):
            amount = world.orb_bundle_size * (bundle_index + 1)
            orbs.add_orb_locations(14,
                                   bundle_index,
                                   access_rule=lambda state, level=level_name, orb_amount=amount:
                                   can_reach_orbs_level(state, player, world, level, orb_amount))
        multiworld.regions.append(orbs)
        main_area.connect(orbs)

    return main_area, behind_oranges_door
