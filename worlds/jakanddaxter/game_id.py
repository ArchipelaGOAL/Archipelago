from enum import IntEnum

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
class Jak1Level(IntEnum):
    FORBIDDEN_JUNGLE = 0
    SENTINEL_BEACH = 1
    MISTY_ISLAND = 2
    PRECURSOR_BASIN = 3
    LOST_PRECURSOR_CITY = 4
    BOGGY_SWAMP = 5
    SPIDER_CAVE = 6
    SNOWY_MOUNTAIN = 7
    GOL_AND_MAIAS_CITADEL = 8

    def __str__(self):
        return self.name.replace("_", " ").title()
