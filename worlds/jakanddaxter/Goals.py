from .Locations import (cell_location_table,
                        cache_location_table,
                        scout_location_table,
                        special_location_table)
from .Levels import level_table
from .Items import (scout_item_table,
                    special_item_table)
from .locs import (CellLocations as Cells,
                   ScoutLocations as Scouts,
                   SpecialLocations as Specials,
                   OrbCacheLocations as Caches)

plant_boss_goal_table = {
    "levels": [
        "Geyser Rock",
        "Sandover Village",
        "Sentinel Beach",
        "Forbidden Jungle",
        "Misty Island",
    ],
    "items": {
        "cells": 34,
        "orbs": 550,
        "scouts": {
            **{Scouts.to_ap_id(k): scout_item_table[k] for k in {95, 75, 7, 20, 28}},
        },
        "specials": {
            **{Specials.to_ap_id(k): special_item_table[k] for k in {5, 4, 2, 17}},
        },
    },
    "locations": {
        "cells": {
            **{Cells.to_ap_id(k): Cells.locGR_cellTable[k] for k in Cells.locGR_cellTable},
            **{Cells.to_ap_id(k): Cells.locSV_cellTable[k] for k in Cells.locSV_cellTable},
            **{Cells.to_ap_id(k): Cells.locFJ_cellTable[k] for k in Cells.locFJ_cellTable},
            **{Cells.to_ap_id(k): Cells.locSB_cellTable[k] for k in Cells.locSB_cellTable},
            **{Cells.to_ap_id(k): Cells.locMI_cellTable[k] for k in Cells.locMI_cellTable},
            **{Cells.to_ap_id(k): Cells.loc7SF_cellTable[k] for k in {95, 75, 7, 20, 28}},
        },
        "scouts": {
            **{Scouts.to_ap_id(k): Scouts.locGR_scoutTable[k] for k in Scouts.locGR_scoutTable},
            **{Scouts.to_ap_id(k): Scouts.locSV_scoutTable[k] for k in Scouts.locSV_scoutTable},
            **{Scouts.to_ap_id(k): Scouts.locFJ_scoutTable[k] for k in Scouts.locFJ_scoutTable},
            **{Scouts.to_ap_id(k): Scouts.locSB_scoutTable[k] for k in Scouts.locSB_scoutTable},
            **{Scouts.to_ap_id(k): Scouts.locMI_scoutTable[k] for k in Scouts.locMI_scoutTable},
        },
        "specials": {
            **{Specials.to_ap_id(k): Specials.loc_specialTable[k] for k in {5, 4, 2, 17}},
        },
        "caches": {
            **{Caches.to_ap_id(k): Caches.loc_orbCacheTable[k] for k in
               {10344, 10369, 11072, 12634, 12635}},
        },
    },
}

klaww_goal_table = {
    "levels": [
        "Geyser Rock",
        "Sandover Village",
        "Sentinel Beach",
        "Forbidden Jungle",
        "Misty Island",
        "Fire Canyon",
        "Rock Village",
        "Lost Precursor City",
        "Boggy Swamp",
        "Precursor Basin",
    ],
    "items": {
        "cells": 66,
        "orbs": 1250,
        "scouts": {
            **{Scouts.to_ap_id(k): scout_item_table[k] for k in {95, 75, 7, 20, 28, 68, 76, 57, 49, 43}},
        },
        "specials": {
            **{Specials.to_ap_id(k): special_item_table[k] for k in {5, 4, 2, 17, 33}},
        },
    },
    "locations": {
        "cells": {
            **{Cells.to_ap_id(k): Cells.locGR_cellTable[k] for k in Cells.locGR_cellTable},
            **{Cells.to_ap_id(k): Cells.locSV_cellTable[k] for k in Cells.locSV_cellTable},
            **{Cells.to_ap_id(k): Cells.locFJ_cellTable[k] for k in Cells.locFJ_cellTable},
            **{Cells.to_ap_id(k): Cells.locSB_cellTable[k] for k in Cells.locSB_cellTable},
            **{Cells.to_ap_id(k): Cells.locMI_cellTable[k] for k in Cells.locMI_cellTable},
            **{Cells.to_ap_id(k): Cells.locFC_cellTable[k] for k in Cells.locFC_cellTable},
            **{Cells.to_ap_id(k): Cells.locRV_cellTable[k] for k in Cells.locRV_cellTable},
            **{Cells.to_ap_id(k): Cells.locPB_cellTable[k] for k in Cells.locPB_cellTable},
            **{Cells.to_ap_id(k): Cells.locLPC_cellTable[k] for k in Cells.locLPC_cellTable},
            **{Cells.to_ap_id(k): Cells.locBS_cellTable[k] for k in Cells.locBS_cellTable},
            **{Cells.to_ap_id(k): Cells.loc7SF_cellTable[k] for k in {95, 75, 7, 20, 28, 68, 76, 57, 49, 43}},
        },
        "scouts": {
            **{Scouts.to_ap_id(k): Scouts.locGR_scoutTable[k] for k in Scouts.locGR_scoutTable},
            **{Scouts.to_ap_id(k): Scouts.locSV_scoutTable[k] for k in Scouts.locSV_scoutTable},
            **{Scouts.to_ap_id(k): Scouts.locFJ_scoutTable[k] for k in Scouts.locFJ_scoutTable},
            **{Scouts.to_ap_id(k): Scouts.locSB_scoutTable[k] for k in Scouts.locSB_scoutTable},
            **{Scouts.to_ap_id(k): Scouts.locMI_scoutTable[k] for k in Scouts.locMI_scoutTable},
            **{Scouts.to_ap_id(k): Scouts.locFC_scoutTable[k] for k in Scouts.locFC_scoutTable},
            **{Scouts.to_ap_id(k): Scouts.locRV_scoutTable[k] for k in Scouts.locRV_scoutTable},
            **{Scouts.to_ap_id(k): Scouts.locPB_scoutTable[k] for k in Scouts.locPB_scoutTable},
            **{Scouts.to_ap_id(k): Scouts.locLPC_scoutTable[k] for k in Scouts.locLPC_scoutTable},
            **{Scouts.to_ap_id(k): Scouts.locBS_scoutTable[k] for k in Scouts.locBS_scoutTable},
        },
        "specials": {
            **{Specials.to_ap_id(k): Specials.loc_specialTable[k] for k in {5, 4, 2, 17, 33}},
        },
        "caches": {
            **{Caches.to_ap_id(k): Caches.loc_orbCacheTable[k] for k in
               {10344, 10369, 11072, 12634, 12635, 10945, 14507, 14838}},
        },
    },
}

# Both Final Boss and 100 Cell Door goals use this table.
citadel_goal_table = {
    "levels": [level for level in level_table],
    "items": {
        "cells": 101,
        "orbs": 2000,
        "scouts": {
            Scouts.to_ap_id(k): scout_item_table[k] for k in scout_item_table
        },
        "specials": {
            Specials.to_ap_id(k): special_item_table[k] for k in special_item_table
        },
    },
    "locations": {
        "cells": cell_location_table,
        "scouts": scout_location_table,
        "specials": special_location_table,
        "caches": cache_location_table,
    },
}
