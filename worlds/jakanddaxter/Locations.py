from BaseClasses import Location, CollectionState
from .GameID import jak1_name
from .locs import (OrbLocations as Orbs,
                   CellLocations as Cells,
                   ScoutLocations as Scouts,
                   SpecialLocations as Specials,
                   OrbCacheLocations as Caches)


class JakAndDaxterLocation(Location):
    game: str = jak1_name

    # In AP 0.5.0, the base Location.can_reach function had its two boolean conditions swapped for a faster
    # short-circuit for better performance. However, Jak seeds actually generate faster using the older method,
    # which has been re-implemented below.
    def can_reach(self, state: CollectionState) -> bool:
        assert self.parent_region, "Can't reach location without region"
        return self.parent_region.can_reach(state) and self.access_rule(state)


# Different tables for location groups.
cell_location_table = {
    **Cells.loc7SF_cellTable,
    **Cells.locGR_cellTable,
    **Cells.locSV_cellTable,
    **Cells.locFJ_cellTable,
    **Cells.locSB_cellTable,
    **Cells.locMI_cellTable,
    **Cells.locFC_cellTable,
    **Cells.locRV_cellTable,
    **Cells.locPB_cellTable,
    **Cells.locLPC_cellTable,
    **Cells.locBS_cellTable,
    **Cells.locMP_cellTable,
    **Cells.locVC_cellTable,
    **Cells.locSC_cellTable,
    **Cells.locSM_cellTable,
    **Cells.locLT_cellTable,
    **Cells.locGMC_cellTable,
}

scout_location_table = {
    **Scouts.locGR_scoutTable,
    **Scouts.locSV_scoutTable,
    **Scouts.locFJ_scoutTable,
    **Scouts.locSB_scoutTable,
    **Scouts.locMI_scoutTable,
    **Scouts.locFC_scoutTable,
    **Scouts.locRV_scoutTable,
    **Scouts.locPB_scoutTable,
    **Scouts.locLPC_scoutTable,
    **Scouts.locBS_scoutTable,
    **Scouts.locMP_scoutTable,
    **Scouts.locVC_scoutTable,
    **Scouts.locSC_scoutTable,
    **Scouts.locSM_scoutTable,
    **Scouts.locLT_scoutTable,
    **Scouts.locGMC_scoutTable,
}

special_location_table = Specials.loc_specialTable
cache_location_table = Caches.loc_orbCacheTable
orb_location_table = Orbs.loc_orbBundleTable

# All Locations
# While we're here, do all the ID conversions needed.
location_table = {
    **{Cells.to_ap_id(k): cell_location_table[k] for k in cell_location_table},
    **{Scouts.to_ap_id(k): scout_location_table[k] for k in scout_location_table},
    **{Specials.to_ap_id(k): special_location_table[k] for k in special_location_table},
    **{Caches.to_ap_id(k): cache_location_table[k] for k in cache_location_table},
    **{Orbs.to_ap_id(k): orb_location_table[k] for k in orb_location_table},
}
