from typing import List
from BaseClasses import CollectionState, MultiWorld
from .RegionBase import JakAndDaxterRegion
from ..Rules import can_free_scout_flies, can_fight


# God help me... here we go.
def build_regions(level_name: str, player: int, multiworld: MultiWorld) -> List[JakAndDaxterRegion]:

    # We need a few helper functions.
    def can_uppercut_spin(state: CollectionState, p: int) -> bool:
        return state.has("Punch Uppercut", p) and state.has("Jump Kick", p)

    def can_triple_jump(state: CollectionState, p: int) -> bool:
        return state.has("Double Jump", p) and state.has("Jump Kick", p)

    # Don't @ me on the name.
    def can_move_fancy(state: CollectionState, p: int) -> bool:
        return can_uppercut_spin(state, p) or can_triple_jump(state, p)

    def can_jump_blockers(state: CollectionState, p: int) -> bool:
        return (state.has("Double Jump", p)
                or state.has("Crouch Jump", p)
                or state.has("Crouch Uppercut", p)
                or state.has("Punch Uppercut", p)
                or state.has("Jump Dive", p))

    main_area = JakAndDaxterRegion("Main Area", player, multiworld, level_name, 0)
    main_area.add_fly_locations([65], access_rule=lambda state: can_free_scout_flies(state, player))

    # We need a few virtual regions like we had for Dark Crystals in Spider Cave.
    # First, a virtual region for the glacier lurkers, who all require combat.
    glacier_lurkers = JakAndDaxterRegion("Glacier Lurkers", player, multiworld, level_name, 0)
    glacier_lurkers.add_cell_locations([61], access_rule=lambda state: can_fight(state, player))

    # Second, a virtual region for the precursor blockers. Unlike the others, this contains orbs:
    # the total number of orbs that sit on top of the blockers. Yes, there are only 8.
    blockers = JakAndDaxterRegion("Precursor Blockers", player, multiworld, level_name, 8)
    blockers.add_cell_locations([66], access_rule=lambda state: can_fight(state, player))

    snowball_canyon = JakAndDaxterRegion("Snowball Canyon", player, multiworld, level_name, 28)

    frozen_box_cave = JakAndDaxterRegion("Frozen Box Cave", player, multiworld, level_name, 12)
    frozen_box_cave.add_cell_locations([67], access_rule=lambda state: state.has("Yellow Eco Switch", player))
    frozen_box_cave.add_fly_locations([327745], access_rule=lambda state:
                                      state.has("Yellow Eco Switch", player)
                                      or can_free_scout_flies(state, player))

    frozen_box_cave_crates = JakAndDaxterRegion("Frozen Box Cave Orb Crates", player, multiworld, level_name, 8)

    # Include 6 orbs on the twin elevator ice ramp.
    ice_skating_rink = JakAndDaxterRegion("Ice Skating Rink", player, multiworld, level_name, 20)
    ice_skating_rink.add_fly_locations([131137], access_rule=lambda state: can_free_scout_flies(state, player))

    flut_flut_course = JakAndDaxterRegion("Flut Flut Course", player, multiworld, level_name, 15)
    flut_flut_course.add_cell_locations([63], access_rule=lambda state: state.has("Flut Flut", player))
    flut_flut_course.add_special_locations([63], access_rule=lambda state: state.has("Flut Flut", player))

    # Includes the bridge from snowball_canyon, the area beneath that bridge, and the areas around the fort.
    fort_exterior = JakAndDaxterRegion("Fort Exterior", player, multiworld, level_name, 20)
    fort_exterior.add_fly_locations([65601, 393281], access_rule=lambda state:
                                    can_free_scout_flies(state, player))

    # Includes the icy island and bridge outside the cave entrance.
    bunny_cave_start = JakAndDaxterRegion("Bunny Cave (Start)", player, multiworld, level_name, 10)

    # Includes the cell and 3 orbs at the exit.
    bunny_cave_end = JakAndDaxterRegion("Bunny Cave (End)", player, multiworld, level_name, 3)
    bunny_cave_end.add_cell_locations([64])

    switch_cave = JakAndDaxterRegion("Yellow Eco Switch Cave", player, multiworld, level_name, 4)
    switch_cave.add_cell_locations([60])
    switch_cave.add_special_locations([60])

    # Only what can be covered by single jump.
    fort_interior = JakAndDaxterRegion("Fort Interior (Main)", player, multiworld, level_name, 19)

    # Reaching the top of the watch tower, getting the fly with the blue eco, and falling down to get the caches.
    fort_interior_caches = JakAndDaxterRegion("Fort Interior (Caches)", player, multiworld, level_name, 51)
    fort_interior_caches.add_fly_locations([196673])
    fort_interior_caches.add_cache_locations([23348, 23349, 23350])

    # Need higher jump.
    fort_interior_base = JakAndDaxterRegion("Fort Interior (Base)", player, multiworld, level_name, 0)
    fort_interior_base.add_fly_locations([262209], access_rule=lambda state:
                                         can_free_scout_flies(state, player))

    # Need farther jump.
    fort_interior_course_end = JakAndDaxterRegion("Fort Interior (Course End)", player, multiworld, level_name, 2)
    fort_interior_course_end.add_cell_locations([62])

    # Wire up the virtual regions first.
    main_area.connect(blockers, rule=lambda state: can_jump_blockers(state, player))
    main_area.connect(glacier_lurkers, rule=lambda state: can_fight(state, player))

    # Yes, the only way into the rest of the level requires advanced movement.
    main_area.connect(snowball_canyon, rule=lambda state:
                      state.has("Roll Jump", player)
                      or can_move_fancy(state, player))

    snowball_canyon.connect(main_area)                              # But you can just jump down and run up the ramp.
    snowball_canyon.connect(bunny_cave_start)                       # Jump down from the glacier troop cliff.
    snowball_canyon.connect(fort_exterior)                          # Jump down, to the left of frozen box cave.
    snowball_canyon.connect(frozen_box_cave, rule=lambda state:     # More advanced movement.
                            can_move_fancy(state, player))

    frozen_box_cave.connect(snowball_canyon, rule=lambda state:                 # Same movement to go back.
                            can_move_fancy(state, player))
    frozen_box_cave.connect(frozen_box_cave_crates, rule=lambda state:          # Same movement to get these crates.
                            state.has("Yellow Eco Switch", player)
                            and can_move_fancy(state, player))
    frozen_box_cave.connect(ice_skating_rink, rule=lambda state:                # Same movement to go forward.
                            can_move_fancy(state, player))

    frozen_box_cave_crates.connect(frozen_box_cave)                             # Semi-virtual region, no moves req'd.

    ice_skating_rink.connect(frozen_box_cave, rule=lambda state:                # Same movement to go back.
                             can_move_fancy(state, player))
    ice_skating_rink.connect(flut_flut_course, rule=lambda state:               # Duh.
                             state.has("Flut Flut", player))
    ice_skating_rink.connect(fort_exterior)                                     # Just slide down the elevator ramp.

    fort_exterior.connect(ice_skating_rink, rule=lambda state:                  # Twin elevators are tough to reach.
                          state.has("Double Jump", player)
                          or state.has("Jump Kick", player))
    fort_exterior.connect(snowball_canyon)                                      # Run across bridge.
    fort_exterior.connect(fort_interior, rule=lambda state:                     # Duh.
                          state.has("Snowy Fort Gate", player))
    fort_exterior.connect(bunny_cave_start)                                     # Run across bridge.
    fort_exterior.connect(switch_cave, rule=lambda state:                       # Yes, blocker jumps work here.
                          can_jump_blockers(state, player))

    fort_interior.connect(fort_interior_caches, rule=lambda state:              # Just need a little height.
                          state.has("Crouch Jump", player)
                          or state.has("Double Jump", player))
    fort_interior.connect(fort_interior_base, rule=lambda state:                # Just need a little height.
                          state.has("Crouch Jump", player)
                          or state.has("Double Jump", player))
    fort_interior.connect(fort_interior_course_end, rule=lambda state:          # Just need a little distance.
                          state.has("Punch Uppercut", player)
                          or state.has("Double Jump", player))

    flut_flut_course.connect(fort_exterior)                                     # Ride the elevator.

    # Must fight way through cave, but there is also a grab-less ledge we must jump over.
    bunny_cave_start.connect(bunny_cave_end, rule=lambda state:
                             can_fight(state, player)
                             and (state.has("Crouch Jump", player)
                                  or state.has("Double Jump", player)))

    # All jump down.
    fort_interior_caches.connect(fort_interior)
    fort_interior_base.connect(fort_interior)
    fort_interior_course_end.connect(fort_interior)
    switch_cave.connect(fort_exterior)
    bunny_cave_end.connect(fort_exterior)

    # I really hope that is everything.
    multiworld.regions.append(main_area)
    multiworld.regions.append(glacier_lurkers)
    multiworld.regions.append(blockers)
    multiworld.regions.append(snowball_canyon)
    multiworld.regions.append(frozen_box_cave)
    multiworld.regions.append(frozen_box_cave_crates)
    multiworld.regions.append(ice_skating_rink)
    multiworld.regions.append(flut_flut_course)
    multiworld.regions.append(fort_exterior)
    multiworld.regions.append(bunny_cave_start)
    multiworld.regions.append(bunny_cave_end)
    multiworld.regions.append(switch_cave)
    multiworld.regions.append(fort_interior)
    multiworld.regions.append(fort_interior_caches)
    multiworld.regions.append(fort_interior_base)
    multiworld.regions.append(fort_interior_course_end)

    return [main_area]
