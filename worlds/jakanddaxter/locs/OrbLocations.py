from ..GameID import jak1_id
from ..Levels import level_table_with_global

# Precursor Orbs are not necessarily given ID's by the game.

# Of the 2000 orbs (or "money") you can pick up, only 1233 are standalone ones you find in the overworld.
# We can identify them by Actor ID's, which run from 549 to 24433. Other actors reside in this range,
# so like Power Cells these are not ordered, nor contiguous, nor exclusively orbs.

# In fact, other ID's in this range belong to actors that spawn orbs when they are activated or when they die,
# like steel crates, orb caches, Spider Cave gnawers, or jumping on the Plant Boss's head. These orbs that spawn
# from parent actors DON'T have an Actor ID themselves - the parent object keeps track of how many of its orbs
# have been picked up.

# In order to deal with this mess, we're creating 2 extra functions that will create and identify Orb Locations for us.
# These will be compatible with both Global Orbsanity and Per-Level Orbsanity, allowing us to create any
# number of Locations depending on the bundle size chosen, while also guaranteeing that each has a unique address.

# We can use 2^15 to offset them from Orb Caches, because Orb Cache ID's max out at (jak1_id + 17792).
orb_offset = 32768


# These helper functions do all the math required to get information about each
# precursor orb and translate its ID between AP and OpenGOAL.
def to_ap_id(game_id: int) -> int:
    if game_id >= jak1_id:
        raise ValueError(f"Attempted to convert {game_id} to an AP ID, but it already is one.")
    return jak1_id + orb_offset + game_id   # Add the offsets and the orb Actor ID.


def to_game_id(ap_id: int) -> int:
    if ap_id < jak1_id:
        raise ValueError(f"Attempted to convert {ap_id} to a Jak 1 ID, but it already is one.")
    return ap_id - jak1_id - orb_offset  # Reverse process, subtract the offsets.


# Use this when the Memory Reader learns that you checked a specific bundle.
# Offset each level by 200 orbs (max number in any level),      {200, 400, ...}
# then divide orb count by bundle size,                         {201, 202, ...}
# then subtract 1.                                              {200, 201, ...}
def find_address(level_index: int, orb_count: int, bundle_size: int) -> int:
    result = (level_index * 200) + (orb_count // bundle_size) - 1
    return result


# Use this when assigning addresses during region generation.
def create_address(level_index: int, bundle_index: int) -> int:
    result = (level_index * 200) + bundle_index
    return result


# What follows is our method of generating all the name/ID pairs for location_name_to_id.
# Remember that not every bundle will be used in the actual seed, we just need this as a static map of strings to ints.
loc_orbBundleTable = {
    create_address(level_table_with_global[name]["level_index"], index): f"{name} Orb Bundle {index + 1}".strip()
    for name in level_table_with_global
    for index in range(level_table_with_global[name]["orbs"])
}
