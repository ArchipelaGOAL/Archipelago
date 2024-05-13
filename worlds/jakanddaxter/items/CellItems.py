from ..GameID import jak1_id

# Power Cells are given ID's between 0 and 116 by the game.

# The game tracks all game-tasks as integers.
# 101 of these ID's correspond directly to power cells, but they are not
# necessarily ordered, nor are they the first 101 in the task list.
# The remaining ones are cutscenes and other events.


# These helper functions do all the math required to get information about each
# power cell and translate its ID between AP and OpenGOAL.
def to_ap_id(game_id: int) -> int:
    assert game_id < jak1_id, f"Attempted to convert {game_id} to an AP ID, but it already is one."
    return jak1_id + game_id


def to_game_id(ap_id: int) -> int:
    assert ap_id >= jak1_id, f"Attempted to convert {ap_id} to a Jak 1 ID, but it already is one."
    return ap_id - jak1_id


# The ID's you see below correspond directly to that cell's game-task ID.

# Geyser Rock
locGR_cellTable = {
    92: "Power Cell - Geyser Path",   # "GR: Find The Cell On The Path",
    93: "Power Cell - Geyser Door",   # "GR: Open The Precursor Door",
    94: "Power Cell - Geyser Cliff",  # "GR: Climb Up The Cliff",
    95: "Power Cell - Geyser Flies",  # "GR: Free 7 Scout Flies"
}

# Sandover Village
locSV_cellTable = {
    11: "Power Cell",  # "SV: Bring 90 Orbs To The Mayor",
    12: "Power Cell",  # "SV: Bring 90 Orbs to Your Uncle",
    10: "Power Cell",  # "SV: Herd The Yakows Into The Pen",
    13: "Power Cell",  # "SV: Bring 120 Orbs To The Oracle (1)",
    14: "Power Cell",  # "SV: Bring 120 Orbs To The Oracle (2)",
    75: "Power Cell",  # "SV: Free 7 Scout Flies"
}

# Forbidden Jungle
locFJ_cellTable = {
    3: "Power Cell",              # "FJ: Connect The Eco Beams",
    4: "Power Cell",              # "FJ: Get To The Top Of The Temple",
    2: "Power Cell - Blue Vent",  # "FJ: Find The Blue Vent Switch",
    6: "Power Cell",              # "FJ: Defeat The Dark Eco Plant",
    5: "Power Cell - Fish Game",  # "FJ: Catch 200 Pounds Of Fish",
    8: "Power Cell",              # "FJ: Follow The Canyon To The Sea",
    9: "Power Cell",              # "FJ: Open The Locked Temple Door",
    7: "Power Cell",              # "FJ: Free 7 Scout Flies"
}

# Sentinel Beach
locSB_cellTable = {
    15: "Power Cell",              # "SB: Unblock The Eco Harvesters",
    17: "Power Cell - Flut Flut",  # "SB: Push The Flut Flut Egg Off The Cliff",
    16: "Power Cell",              # "SB: Get The Power Cell From The Pelican",
    18: "Power Cell",              # "SB: Chase The Seagulls",
    19: "Power Cell",              # "SB: Launch Up To The Cannon Tower",
    21: "Power Cell",              # "SB: Explore The Beach",
    22: "Power Cell",              # "SB: Climb The Sentinel",
    20: "Power Cell",              # "SB: Free 7 Scout Flies"
}

# Misty Island
locMI_cellTable = {
    23: "Power Cell",  # "MI: Catch The Sculptor's Muse",
    24: "Power Cell",  # "MI: Climb The Lurker Ship",
    26: "Power Cell",  # "MI: Stop The Cannon",
    25: "Power Cell",  # "MI: Return To The Dark Eco Pool",
    27: "Power Cell",  # "MI: Destroy the Balloon Lurkers",
    29: "Power Cell",  # "MI: Use Zoomer To Reach Power Cell",
    30: "Power Cell",  # "MI: Use Blue Eco To Reach Power Cell",
    28: "Power Cell",  # "MI: Free 7 Scout Flies"
}

# Fire Canyon
locFC_cellTable = {
    69: "Power Cell",  # "FC: Reach The End Of Fire Canyon",
    68: "Power Cell",  # "FC: Free 7 Scout Flies"
}

# Rock Village
locRV_cellTable = {
    31: "Power Cell",  # "RV: Bring 90 Orbs To The Gambler",
    32: "Power Cell",  # "RV: Bring 90 Orbs To The Geologist",
    33: "Power Cell",  # "RV: Bring 90 Orbs To The Warrior",
    34: "Power Cell",  # "RV: Bring 120 Orbs To The Oracle (1)",
    35: "Power Cell",  # "RV: Bring 120 Orbs To The Oracle (2)",
    76: "Power Cell",  # "RV: Free 7 Scout Flies"
}

# Precursor Basin
locPB_cellTable = {
    54: "Power Cell",  # "PB: Herd The Moles Into Their Hole",
    53: "Power Cell",  # "PB: Catch The Flying Lurkers",
    52: "Power Cell",  # "PB: Beat Record Time On The Gorge",
    56: "Power Cell",  # "PB: Get The Power Cell Over The Lake",
    55: "Power Cell",  # "PB: Cure Dark Eco Infected Plants",
    58: "Power Cell",  # "PB: Navigate The Purple Precursor Rings",
    59: "Power Cell",  # "PB: Navigate The Blue Precursor Rings",
    57: "Power Cell",  # "PB: Free 7 Scout Flies"
}

# Lost Precursor City
locLPC_cellTable = {
    47: "Power Cell - Sunken Room",   # "LPC: Raise The Chamber",
    45: "Power Cell",                 # "LPC: Follow The Colored Pipes",
    46: "Power Cell - Sunken Slide",  # "LPC: Reach The Bottom Of The City",
    48: "Power Cell",                 # "LPC: Quickly Cross The Dangerous Pool",
    44: "Power Cell",                 # "LPC: Match The Platform Colors",
    50: "Power Cell",                 # "LPC: Climb The Slide Tube",
    51: "Power Cell",                 # "LPC: Reach The Center Of The Complex",
    49: "Power Cell",                 # "LPC: Free 7 Scout Flies"
}

# Boggy Swamp
locBS_cellTable = {
    37: "Power Cell",  # "BS: Ride The Flut Flut",
    36: "Power Cell",  # "BS: Protect Farthy's Snacks",
    38: "Power Cell",  # "BS: Defeat The Lurker Ambush",
    39: "Power Cell",  # "BS: Break The Tethers To The Zeppelin (1)",
    40: "Power Cell",  # "BS: Break The Tethers To The Zeppelin (2)",
    41: "Power Cell",  # "BS: Break The Tethers To The Zeppelin (3)",
    42: "Power Cell",  # "BS: Break The Tethers To The Zeppelin (4)",
    43: "Power Cell",  # "BS: Free 7 Scout Flies"
}

# Mountain Pass
locMP_cellTable = {
    86:  "Power Cell",  # "MP: Defeat Klaww",
    87:  "Power Cell",  # "MP: Reach The End Of The Mountain Pass",
    110: "Power Cell",  # "MP: Find The Hidden Power Cell",
    88:  "Power Cell",  # "MP: Free 7 Scout Flies"
}

# Volcanic Crater
locVC_cellTable = {
    96:  "Power Cell",  # "VC: Bring 90 Orbs To The Miners (1)",
    97:  "Power Cell",  # "VC: Bring 90 Orbs To The Miners (2)",
    98:  "Power Cell",  # "VC: Bring 90 Orbs To The Miners (3)",
    99:  "Power Cell",  # "VC: Bring 90 Orbs To The Miners (4)",
    100: "Power Cell",  # "VC: Bring 120 Orbs To The Oracle (1)",
    101: "Power Cell",  # "VC: Bring 120 Orbs To The Oracle (2)",
    74:  "Power Cell",  # "VC: Find The Hidden Power Cell",
    77:  "Power Cell",  # "VC: Free 7 Scout Flies"
}

# Spider Cave
locSC_cellTable = {
    78: "Power Cell",  # "SC: Use Your Goggles To Shoot The Gnawing Lurkers",
    79: "Power Cell",  # "SC: Destroy The Dark Eco Crystals",
    80: "Power Cell",  # "SC: Explore The Dark Cave",
    81: "Power Cell",  # "SC: Climb The Giant Robot",
    82: "Power Cell",  # "SC: Launch To The Poles",
    83: "Power Cell",  # "SC: Navigate The Spider Tunnel",
    84: "Power Cell",  # "SC: Climb the Precursor Platforms",
    85: "Power Cell",  # "SC: Free 7 Scout Flies"
}

# Snowy Mountain
locSM_cellTable = {
    60: "Power Cell - Yellow Vent",  # "SM: Find The Yellow Vent Switch",
    61: "Power Cell",                # "SM: Stop The 3 Lurker Glacier Troops",
    66: "Power Cell",                # "SM: Deactivate The Precursor Blockers",
    67: "Power Cell",                # "SM: Open The Frozen Crate",
    63: "Power Cell - Fort Gate",    # "SM: Open The Lurker Fort Gate",
    62: "Power Cell",                # "SM: Get Through The Lurker Fort",
    64: "Power Cell",                # "SM: Survive The Lurker Infested Cave",
    65: "Power Cell",                # "SM: Free 7 Scout Flies"
}

# Lava Tube
locLT_cellTable = {
    89: "Power Cell",  # "LT: Cross The Lava Tube",
    90: "Power Cell",  # "LT: Free 7 Scout Flies"
}

# Gol and Maias Citadel
locGMC_cellTable = {
    71: "Power Cell - Blue Sage",    # "GMC: Free The Blue Sage",
    72: "Power Cell - Red Sage",     # "GMC: Free The Red Sage",
    73: "Power Cell - Yellow Sage",  # "GMC: Free The Yellow Sage",
    70: "Power Cell - Green Sage",   # "GMC: Free The Green Sage",
    91: "Power Cell",                # "GMC: Free 7 Scout Flies"
}
