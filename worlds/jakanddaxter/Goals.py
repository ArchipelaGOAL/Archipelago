from .Locations import cache_location_table
from .Items import scout_item_table, special_item_table
from .locs import (ScoutLocations as Scouts,
                   SpecialLocations as Specials,
                   OrbCacheLocations as Caches)

# These Goal Tables tell us how many items/locations we need to generate, and which ones, depending on the completion
# condition chosen in the player options. Some items/locations are fungible and only need a count, while others are
# unique and need a specific list. These tables do not include move items, that will be handled separately, but they
# do include orb caches.

# All items and locations prior to Fire Canyon.
plant_boss_goal_table = {
    "cells": 34,
    "orbs": 550,
    "caches": 5,
    "scouts": {
        **{Scouts.to_ap_id(k): scout_item_table[k] for k in
           {95, 75, 7, 20, 28}},
    },
    "specials": {
        **{Specials.to_ap_id(k): special_item_table[k] for k in
           {5, 4, 2, 17}},
    },
}

# All items and locations prior to Mountain Pass.
klaww_goal_table = {
    "cells": 66,
    "orbs": 1250,
    "caches": 8,
    "scouts": {
        **{Scouts.to_ap_id(k): scout_item_table[k] for k in
           {95, 75, 7, 20, 28, 68, 76, 57, 49, 43}},
    },
    "specials": {
        **{Specials.to_ap_id(k): special_item_table[k] for k in
           {5, 4, 2, 17, 33}},
    },
}

# All items and locations period.
# Both Final Boss and 100 Cell Door goals use this table.
citadel_goal_table = {
    "cells": 101,
    "orbs": 2000,
    "caches": 14,
    "scouts": {
        Scouts.to_ap_id(k): scout_item_table[k] for k in scout_item_table
    },
    "specials": {
        Specials.to_ap_id(k): special_item_table[k] for k in special_item_table
    },
}
