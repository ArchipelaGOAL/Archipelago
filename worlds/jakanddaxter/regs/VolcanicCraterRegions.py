from typing import List
from BaseClasses import MultiWorld
from .RegionBase import JakAndDaxterRegion
from .. import JakAndDaxterOptions, EnableOrbsanity, JakAndDaxterWorld
from ..Rules import can_free_scout_flies
from ..locs import ScoutLocations as Scouts


def build_regions(level_name: str, world: JakAndDaxterWorld, multiworld: MultiWorld, options: JakAndDaxterOptions, player: int) -> List[JakAndDaxterRegion]:

    total_trade_orbs = (9 * options.citizen_orb_trade_amount) + (6 * options.oracle_orb_trade_amount)

    # No area is inaccessible in VC even with only running and jumping.
    main_area = JakAndDaxterRegion("Main Area", player, multiworld, level_name, 50)
    main_area.add_cell_locations([96], access_rule=lambda state: world.can_trade(state, total_trade_orbs, None))
    main_area.add_cell_locations([97], access_rule=lambda state: world.can_trade(state, total_trade_orbs, 96))
    main_area.add_cell_locations([98], access_rule=lambda state: world.can_trade(state, total_trade_orbs, 97))
    main_area.add_cell_locations([99], access_rule=lambda state: world.can_trade(state, total_trade_orbs, 98))
    main_area.add_cell_locations([100], access_rule=lambda state: world.can_trade(state, total_trade_orbs, None))
    main_area.add_cell_locations([101], access_rule=lambda state: world.can_trade(state, total_trade_orbs, 100))

    # Hidden Power Cell: you can carry yellow eco from Spider Cave just by running and jumping
    # and using your Goggles to shoot the box (you do not need Punch to shoot from FP mode).
    main_area.add_cell_locations([74])

    # No blue eco sources in this area, all boxes must be broken by hand (yellow eco can't be carried far enough).
    main_area.add_fly_locations(Scouts.locVC_scoutTable.keys(), access_rule=lambda state:
                                can_free_scout_flies(state, player))

    # Approach the gondola to get this check.
    main_area.add_special_locations([105])

    multiworld.regions.append(main_area)

    # If Per-Level Orbsanity is enabled, build the special Orbsanity Region. This is a virtual region always
    # accessible to Main Area. The Locations within are automatically checked when you collect enough orbs.
    if options.enable_orbsanity == EnableOrbsanity.option_per_level:
        orbs = JakAndDaxterRegion("Orbsanity", player, multiworld, level_name)

        bundle_size = options.level_orbsanity_bundle_size.value
        bundle_count = 50 // bundle_size
        for bundle_index in range(bundle_count):
            orbs.add_orb_locations(11,
                                   bundle_index,
                                   access_rule=lambda state, bundle=bundle_index:
                                   world.count_reachable_orbs(state, level_name) >= (bundle_size * (bundle + 1)))
        multiworld.regions.append(orbs)
        main_area.connect(orbs)

    return [main_area]
