from BaseClasses import Item
from .GameID import jak1_name
from .locs import CellLocations as Cells, ScoutLocations as Scouts, SpecialLocations as Specials


class JakAndDaxterItem(Item):
    game: str = jak1_name


# The following are generic, fungible, interchangeable items.
# One power cell is indistinguishable from every other power cell.
# Ditto scout flies, minus the fact they are tied to their respective levels.
#    Take note that their ID is equal to their respective power cell's ID.
# Ditto Precursor Orbs -- TODO ^^.
cell_item_table = {
    0:  "Power Cell",
}

scout_item_table = {
    95: "Scout Fly - GR",
    75: "Scout Fly - SV",
    7:  "Scout Fly - FJ",
    20: "Scout Fly - SB",
    28: "Scout Fly - MI",
    68: "Scout Fly - FC",
    76: "Scout Fly - RV",
    57: "Scout Fly - PB",
    49: "Scout Fly - LPC",
    43: "Scout Fly - BS",
    88: "Scout Fly - MP",
    77: "Scout Fly - VC",
    85: "Scout Fly - SC",
    65: "Scout Fly - SM",
    90: "Scout Fly - LT",
    91: "Scout Fly - GMC",
}

# orb_item_table = {
#     ???: "Precursor Orb",
# }

# These are special items representing unique unlocks in the world.
# They are not tied to their respective tasks or power cells, they are
# entirely standalone and thus can be added to the item pool as independent items.
special_item_table = {
    5: "Fisherman's Boat",
    4: "Jungle Elevator",
    2: "Blue Eco Switch",
    17: "Flut Flut",
    60: "Yellow Eco Switch",
    63: "Snowy Fort Gate",
    71: "Freed Blue Sage",
    72: "Freed Red Sage",
    73: "Freed Yellow Sage",
    70: "Freed Green Sage",
}

# All Items
# While we're here, do all the ID conversions needed.
item_table = {
    **{Cells.to_ap_id(k): cell_item_table[k] for k in cell_item_table},
    **{Scouts.to_ap_id(k): scout_item_table[k] for k in scout_item_table},
    # **{Orbs.to_ap_id(k): orb_item_table[k] for k in orb_item_table},
    **{Specials.to_ap_id(k): special_item_table[k] for k in special_item_table},
}
