import Utils

# All Jak And Daxter Archipelago IDs must be offset by this number.
jak1_id = 741000000

# This is maximum ID we will allow.
jak1_max = jak1_id + 999999

# The name of the game.
jak1_name = "Jak and Daxter: The Precursor Legacy"

# The executable name of the GOAL Kernel.
jak1_gk = "gk" + (".exe" if Utils.is_windows else "")

# The executable name of the GOAL Compiler.
jak1_goalc = "goalc" + (".exe" if Utils.is_windows else "")

# These level ids are arbitrary, and used for level randomization.
jak1_level_ids = {
    "FJ": 0,
    "SB": 1,
    "MI": 2,
    "PB": 3,
    "LPC": 4,
    "BS": 5,
    "SC": 6,
    "SM": 7,
}