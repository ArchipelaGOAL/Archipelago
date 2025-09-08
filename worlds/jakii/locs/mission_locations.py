from typing import Callable, Optional
from worlds.jakii.rules import (slums_to_port, slums_to_stadium, slums_to_market, slums_to_landing, slums_to_nest,
                                any_gun)


class Jak2MissionData:
    mission_id: int  # Mission ID is how Archipelago identifies the location.
    task_id: int  # Task ID is how GOAL identifies the location.
    name: str
    rule: Callable

    def __init__(self, mission_id: int, task_id: int, name: str, rule: Optional[Callable] = None):
        self.mission_id = mission_id
        self.task_id = task_id
        self.name = name
        if rule:
            self.rule = rule
        else:
            self.rule = lambda state, player: True


class Jak2SideMissionData:
    mission_id: int  # Mission ID is how Archipelago identifies the location.
    task_id: int  # Task ID is how GOAL identifies the location.
    name: str
    rule: Callable

    def __init__(self, mission_id: int, task_id: int, name: str, rule: Optional[Callable] = None):
        self.mission_id = mission_id
        self.task_id = task_id
        self.name = name
        if rule:
            self.rule = rule
        else:
            self.rule = lambda state, player: True


# Names for Missions are taken directly from the game
main_mission_table = {
    # Act 1
    1: Jak2MissionData(mission_id=1, task_id=6, name="Escape From Prison"),
    2: Jak2MissionData(mission_id=2, task_id=7, name="Protect Kor and Kid",
                       rule=lambda state, player:
                       state.has("Dark Jak", player)),
    3: Jak2MissionData(mission_id=3, task_id=9, name="Retrieve Banner from Dead Town"),
    4: Jak2MissionData(mission_id=4, task_id=10, name="Find Pumping Station Valve"),
    5: Jak2MissionData(mission_id=5, task_id=11, name="Blow up Ammo at Fortress"),
    6: Jak2MissionData(mission_id=6, task_id=12, name="Make delivery to Hip Hog Saloon",
                       rule=lambda state, player:
                       state.has("Red Security Pass", player)
                       or state.has_all(("Green Security Pass", "Yellow Security Pass"), player)),
    7: Jak2MissionData(mission_id=7, task_id=13, name="Beat Scatter Gun Course",
                       rule=lambda state, player:
                       slums_to_port(state, player)
                       and state.has("Scatter Gun", player)),
    8: Jak2MissionData(mission_id=8, task_id=14, name="Protect Sig at Pumping Station",
                       rule=lambda state, player:
                       slums_to_port(state, player)
                       and any_gun(state, player)),
    9: Jak2MissionData(mission_id=9, task_id=15, name="Destroy Turrets in Sewers",
                       rule=lambda state, player:
                       slums_to_port(state, player)
                       and any_gun(state, player)),
    10: Jak2MissionData(mission_id=10, task_id=16, name="Rescue Vin at Strip Mine",
                        rule=lambda state, player:
                        slums_to_port(state, player)
                        and any_gun(state, player)),
    11: Jak2MissionData(mission_id=11, task_id=17, name="Find Pumping Station Patrol",
                        rule=lambda state, player: any_gun(state, player)),
    12: Jak2MissionData(mission_id=12, task_id=18, name="Find Lens in Mountain Temple",
                        rule=lambda state, player:
                        slums_to_market(state, player)
                        and state.has_any(("Scatter Gun", "Blaster", "Vulcan Fury"), player)),
    13: Jak2MissionData(mission_id=13, task_id=19, name="Find Gear in Mountain Temple",
                        rule=lambda state, player:
                        slums_to_market(state, player)
                        and state.has_any(("Scatter Gun", "Blaster", "Vulcan Fury"), player)),
    14: Jak2MissionData(mission_id=14, task_id=20, name="Find Shard in Mountain Temple",
                        rule=lambda state, player:
                        slums_to_market(state, player)
                        and state.has_any(("Scatter Gun", "Blaster", "Vulcan Fury"), player)),
    15: Jak2MissionData(mission_id=15, task_id=22, name="Beat Time to Race Garage",
                        rule=lambda state, player:
                        slums_to_port(state, player)
                        and (state.has_all(("Red Security Pass", "Green Security Pass"), player)
                             or state.has("Yellow Security Pass", player))),
    16: Jak2MissionData(mission_id=16, task_id=23, name="Win JET-Board Stadium Challenge",
                        rule=lambda state, player:
                        slums_to_stadium(state, player)),
    17: Jak2MissionData(mission_id=17, task_id=24, name="Collect Money for Krew",
                        rule=lambda state, player:
                        slums_to_port(state, player)),
    18: Jak2MissionData(mission_id=18, task_id=25, name="Beat Blaster Gun Course",
                        rule=lambda state, player:
                        slums_to_port(state, player)
                        and state.has("Blaster", player)),
    19: Jak2MissionData(mission_id=19, task_id=26, name="Destroy Eggs at Drill Platform",
                        rule=lambda state, player:
                        slums_to_port(state, player)
                        and any_gun(state, player)
                        and state.has("Gunpod", player)),
    20: Jak2MissionData(mission_id=20, task_id=27, name="Turn on 5 Power Switches",
                        rule=lambda state, player:
                        slums_to_port(state, player)
                        and ((any_gun(state, player)
                              and state.has("Red Security Pass", player))
                             or (any_gun(state, player)
                                 and state.has_all(("Green Security Pass", "Yellow Security Pass"), player)))),
    21: Jak2MissionData(mission_id=21, task_id=28, name="Ride Elevator up to Palace",
                        rule=lambda state, player:
                        any_gun(state, player)
                        and slums_to_stadium(state, player)),
    22: Jak2MissionData(mission_id=22, task_id=29, name="Defeat Baron at Palace",
                        rule=lambda state, player:
                        any_gun(state, player)
                        and slums_to_stadium(state, player)),
    # Act 2 (Palace Baron Fight Complete)
    23: Jak2MissionData(mission_id=23, task_id=30, name="Shuttle Underground Fighters"),
    24: Jak2MissionData(mission_id=24, task_id=31, name="Protect Site in Dead Town",
                        rule=lambda state, player:
                        any_gun(state, player)),
    25: Jak2MissionData(mission_id=25, task_id=33, name="Catch Scouts in Haven Forest",
                        rule=lambda state, player:
                        slums_to_market(state, player)
                        and state.has("JET-Board", player)),
    26: Jak2MissionData(mission_id=26, task_id=34, name="Escort Kid to Power Station",
                        rule=lambda state, player:
                        state.has("Red Security Pass", player)),
    27: Jak2MissionData(mission_id=27, task_id=35, name="Destroy Equipment at Dig",
                        rule=lambda state, player:
                        slums_to_port(state, player)
                        and state.has("JET-Board", player)),
    28: Jak2MissionData(mission_id=28, task_id=36, name="Blow up Strip Mine Eco Wells",
                        rule=lambda state, player:
                        slums_to_port(state, player)
                        and state.has("JET-Board", player)),
    29: Jak2MissionData(mission_id=29, task_id=37, name="Destroy Ship at Drill Platform",
                        rule=lambda state, player:
                        slums_to_port(state, player)
                        and state.has("Gunpod", player)),
    30: Jak2MissionData(mission_id=30, task_id=38, name="Destroy Cargo in Port",
                        rule=lambda state, player:
                        slums_to_port(state, player)
                        and state.has("JET-Board", player)),
    31: Jak2MissionData(mission_id=31, task_id=39, name="Rescue Lurkers for Brutter #1",
                        rule=lambda state, player:
                        slums_to_port(state, player)
                        and any_gun(state, player)
                        and state.has("Yellow Security Pass", player)),
    32: Jak2MissionData(mission_id=32, task_id=40, name="Drain Sewers to find Statue",
                        rule=lambda state, player:
                        slums_to_port(state, player)
                        and state.has("JET-Board", player)),
    33: Jak2MissionData(mission_id=33, task_id=41, name="Hunt Haven Forest Metal Heads",
                        rule=lambda state, player:
                        slums_to_port(state, player)
                        and any_gun(state, player)
                        and state.has("Yellow Security Pass", player)),
    34: Jak2MissionData(mission_id=34, task_id=42, name="Intercept Tanker",
                        rule=lambda state, player:
                        slums_to_market(state, player)
                        and (any_gun(state, player)
                             or state.has("Dark Jak", player))),
    35: Jak2MissionData(mission_id=35, task_id=43, name="Win Class 3 Race at Stadium",
                        rule=lambda state, player:
                        slums_to_stadium(state, player)),
    36: Jak2MissionData(mission_id=36, task_id=44, name="Get Seal Piece at Water Slums",
                        rule=lambda state, player:
                        any_gun(state, player)
                        or state.has("JET-Board", player)),
    37: Jak2MissionData(mission_id=37, task_id=45, name="Get Seal Piece at Dig",
                        rule=lambda state, player:
                        slums_to_market(state, player)
                        and any_gun(state, player)
                        and state.has("JET-Board", player)),
    38: Jak2MissionData(mission_id=38, task_id=46, name="Destroy 5 HellCat Cruisers",
                        rule=lambda state, player:
                        state.has("Red Security Pass", player)
                        and any_gun(state, player)),
    39: Jak2MissionData(mission_id=39, task_id=47, name="Beat Onin Game",
                        rule=lambda state, player:
                        slums_to_market(state, player)),
    40: Jak2MissionData(mission_id=40, task_id=48, name="Use items in No Man's Canyon",
                        rule=lambda state, player:
                        slums_to_market(state, player)
                        and state.has("JET-Board", player)
                        and state.has_all(("Seal Piece #1", "Seal Piece #2", "Seal Piece #3"), player)),
    41: Jak2MissionData(mission_id=41, task_id=49, name="Pass the first Test of Manhood",
                        rule=lambda state, player:
                        slums_to_market(state, player)
                        and state.has_all(("Lens", "Gear", "Shard"), player)),
    42: Jak2MissionData(mission_id=42, task_id=50, name="Pass the second Test of Manhood",
                        rule=lambda state, player:
                        slums_to_market(state, player)
                        and state.has_all(("Lens", "Gear", "Shard"), player)),
    43: Jak2MissionData(mission_id=43, task_id=51, name="Defeat Baron in Mar's Tomb",
                        rule=lambda state, player:
                        slums_to_market(state, player)
                        and any_gun(state, player)
                        and state.has_all(("Lens", "Gear", "Shard"), player)),
    # Act 3 (Tomb Baron Fight Complete)
    44: Jak2MissionData(mission_id=44, task_id=52, name="Rescue Friends in Fortress",
                        rule=lambda state, player:
                        any_gun(state, player)
                        and state.has("JET-Board", player)),
    45: Jak2MissionData(mission_id=45, task_id=53, name="Escort men through Sewers",
                        rule=lambda state, player:
                        slums_to_port(state, player)
                        and any_gun(state, player)),
    46: Jak2MissionData(mission_id=46, task_id=55, name="Win Class 2 Race at Stadium",
                        rule=lambda state, player:
                        slums_to_stadium(state, player)),
    47: Jak2MissionData(mission_id=47, task_id=56, name="Protect Hideout from Bombots",
                        rule=lambda state, player:
                        state.has_all(("Red Security Pass", "Vulcan Fury"), player)),
    48: Jak2MissionData(mission_id=48, task_id=57, name="Beat Erol in Race Challenge",
                        rule=lambda state, player:
                        slums_to_port(state, player)
                        and state.has("Yellow Security Pass", player)),
    49: Jak2MissionData(mission_id=49, task_id=58, name="Destroy Eggs in Strip Mine",
                        rule=lambda state, player:
                        slums_to_port(state, player)
                        and state.has("JET-Board", player)),
    50: Jak2MissionData(mission_id=50, task_id=59, name="Get Life Seed in Dead Town",
                        rule=lambda state, player:
                        any_gun(state, player)
                        and state.has("Titan Suit", player)),
    51: Jak2MissionData(mission_id=51, task_id=60, name="Protect Samos in Haven Forest",
                        rule=lambda state, player:
                        slums_to_market(state, player)
                        and any_gun(state, player)
                        and state.has("Life Seed", player)),
    52: Jak2MissionData(mission_id=52, task_id=61, name="Destroy Drill Platform Tower",
                        rule=lambda state, player:
                        slums_to_port(state, player)
                        and (state.has("Titan Suit", player)
                             and state.has_any(("Blaster", "Vulcan Fury"), player))),
    53: Jak2MissionData(mission_id=53, task_id=62, name="Rescue Lurkers for Brutter #2",
                        rule=lambda state, player:
                        slums_to_market(state, player)
                        and (state.has("Yellow Security Pass", player))
                        and any_gun(state, player)),
    54: Jak2MissionData(mission_id=54, task_id=63, name="Win Class 1 Race at Stadium",
                        rule=lambda state, player:
                        slums_to_stadium(state, player)),
    55: Jak2MissionData(mission_id=55, task_id=64, name="Explore Palace",
                        rule=lambda state, player:
                        slums_to_market(state, player)
                        and state.has_all(("JET-Board", "Purple Security Pass"), player)
                        and any_gun(state, player)),
    56: Jak2MissionData(mission_id=56, task_id=65, name="Get Heart of Mar in Weapons Lab",
                        rule=lambda state, player:
                        slums_to_landing(state, player)
                        and state.has("Black Security Pass", player)
                        and any_gun(state, player)),
    57: Jak2MissionData(mission_id=57, task_id=66, name="Beat Krew in Weapons Lab",
                        rule=lambda state, player:
                        slums_to_landing(state, player)
                        and state.has("Black Security Pass", player)
                        and any_gun(state, player)),
    58: Jak2MissionData(mission_id=58, task_id=67, name="Beat the Metal Head Mash Game",
                        rule=lambda state, player:
                        slums_to_port(state, player)),
    59: Jak2MissionData(mission_id=59, task_id=68, name="Find Sig in Under Port",
                        rule=lambda state, player:
                        slums_to_port(state, player)
                        and state.has_all(("Ruby Key", "Titan Suit"), player)),
    60: Jak2MissionData(mission_id=60, task_id=69, name="Escort Sig in Under Port",
                        rule=lambda state, player:
                        slums_to_port(state, player)
                        and state.has_all(("Ruby Key", "Titan Suit"), player)
                        and any_gun(state, player)),
    61: Jak2MissionData(mission_id=61, task_id=70, name="Defend Stadium",
                        rule=lambda state, player:
                        slums_to_stadium(state, player)
                        and state.has_all(("Heart of Mar", "Time Map", "Rift Rider"), player)
                        and any_gun(state, player)),
    62: Jak2MissionData(mission_id=62, task_id=71, name="Check the Construction Site",
                        rule=lambda state, player:
                        slums_to_port(state, player)),
    63: Jak2MissionData(mission_id=63, task_id=72, name="Break Barrier at Nest",
                        rule=lambda state, player:
                        slums_to_nest(state, player)
                        and state.has("Precursor Stone", player)
                        and any_gun(state, player)),
    64: Jak2MissionData(mission_id=64, task_id=73, name="Attack the Metal Head Nest",
                        rule=lambda state, player:
                        slums_to_nest(state, player)
                        and state.has("Precursor Stone", player)
                        and any_gun(state, player)),
    65: Jak2MissionData(mission_id=65, task_id=74, name="Destroy Metal Kor at Nest",
                        rule=lambda state, player:
                        slums_to_nest(state, player)
                        and state.has("Precursor Stone", player)
                        and any_gun(state, player))
}


main_tasks_to_missions = {miss.task_id: miss for _, miss in main_mission_table.items()}


# Names of Side Missions are taken from the Fandom Jak II Wiki
# ID numbers are precalculated and offset by 100 to distinguish them from main missions.
side_mission_table = {
    # Orb Searches
    101: Jak2SideMissionData(mission_id=101, task_id=78, name="Orb Search 1 (Computer #2)"),
    102: Jak2SideMissionData(mission_id=102, task_id=79, name="Orb Search 2 (Computer #3)",
                             rule=lambda state, player:
                             slums_to_port(state, player)),
    103: Jak2SideMissionData(mission_id=103, task_id=80, name="Orb Search 3 (Computer #4)",
                             rule=lambda state, player:
                             slums_to_port(state, player)),
    104: Jak2SideMissionData(mission_id=104, task_id=81, name="Orb Search 4 (Computer #5)"),
    105: Jak2SideMissionData(mission_id=105, task_id=85, name="Orb Search 5 (Computer #9)",
                             rule=lambda state, player:
                             slums_to_market(state, player)),
    106: Jak2SideMissionData(mission_id=106, task_id=86, name="Orb Search 6 (Computer #10)",
                             rule=lambda state, player:
                             slums_to_market(state, player)),
    107: Jak2SideMissionData(mission_id=107, task_id=88, name="Orb Search 7 (Computer #11)",
                             rule=lambda state, player:
                             slums_to_market(state, player)),
    108: Jak2SideMissionData(mission_id=108, task_id=89, name="Orb Search 8 (Computer #12)",
                             rule=lambda state, player:
                             slums_to_market(state, player)),
    109: Jak2SideMissionData(mission_id=109, task_id=90, name="Orb Search 9 (Computer #6)",
                             rule=lambda state, player:
                             slums_to_stadium(state, player)),
    110: Jak2SideMissionData(mission_id=110, task_id=92, name="Orb Search 10 (Computer #14)",
                             rule=lambda state, player:
                             slums_to_port(state, player)),
    111: Jak2SideMissionData(mission_id=111, task_id=93, name="Orb Search 11 (Computer #15)",
                             rule=lambda state, player:
                             slums_to_stadium(state, player)),
    112: Jak2SideMissionData(mission_id=112, task_id=95, name="Orb Search 12 (Computer #7)",
                             rule=lambda state, player:
                             state.has_all(("Red Security Pass", "Yellow Security Pass"), player)
                             or slums_to_market(state, player)),
    113: Jak2SideMissionData(mission_id=113, task_id=97, name="Orb Search 13 (Computer #16)",
                             rule=lambda state, player:
                             state.has("Green Security Pass", player)),
    114: Jak2SideMissionData(mission_id=114, task_id=98, name="Orb Search 14 (Computer #17)",
                             rule=lambda state, player:
                             slums_to_stadium(state, player)),
    115: Jak2SideMissionData(mission_id=115, task_id=99, name="Orb Search 15 (Computer #18)",
                             rule=lambda state, player:
                             slums_to_market(state, player)),
    # Ring Races
    116: Jak2SideMissionData(mission_id=116, task_id=77, name="Ring Race 1 (Computer #1)"),
    117: Jak2SideMissionData(mission_id=117, task_id=84, name="Ring Race 2 (Computer #8)",
                             rule=lambda state, player:
                             slums_to_port(state, player)
                             or state.has("Yellow Security Pass", player)),
    118: Jak2SideMissionData(mission_id=118, task_id=94, name="Ring Race 3 (Computer #1)",
                             rule=lambda state, player:
                             state.has("Red Security Pass", player)),
    # Collect-em-alls
    119: Jak2SideMissionData(mission_id=119, task_id=82, name="Collection 1 (Computer #6)",
                             rule=lambda state, player:
                             slums_to_stadium(state, player)),
    120: Jak2SideMissionData(mission_id=120, task_id=91, name="Collection 2 (Computer #13)",
                             rule=lambda state, player:
                             slums_to_stadium(state, player)),
    121: Jak2SideMissionData(mission_id=121, task_id=100, name="Collection 3 (Computer #12)",
                             rule=lambda state, player:
                             slums_to_market(state, player)),
    # Missions Turned Side Missions
    122: Jak2SideMissionData(mission_id=122, task_id=83, name="Deliver Package Side Mission (Computer #7)"),
    123: Jak2SideMissionData(mission_id=123, task_id=87, name="Shuttle Underground Fighters Side Mission (Computer #7)",
                             rule=lambda state, player:
                             state.has_all(("Red Security Pass", "Yellow Security Pass"), player)),
    124: Jak2SideMissionData(mission_id=124, task_id=96, name="Destroy Blast Bots Side Mission (Computer #7)",
                             rule=lambda state, player:
                             slums_to_market(state, player)
                             or state.has("Yellow Security Pass", player)),
    # Extra Race Missions
    125: Jak2SideMissionData(mission_id=125, task_id=25, name="Erol Race Side Mission",
                             rule=lambda state, player:
                             slums_to_port(state, player)
                             or state.has("Yellow Security Pass", player)),
    126: Jak2SideMissionData(mission_id=126, task_id=26, name="Port Race Side Mission",
                             rule=lambda state, player:
                             slums_to_port(state, player)),
    # Stadium Challenges
    127: Jak2SideMissionData(mission_id=127, task_id=103, name="JET-Board Stadium Challenge Side Mission",
                             rule=lambda state, player:
                             state.has("JET-Board", player)),
    128: Jak2SideMissionData(mission_id=128, task_id=104, name="Class 3 Race Side Mission (Computer by Stadium)",
                             rule=lambda state, player:
                             slums_to_stadium(state, player)),
    129: Jak2SideMissionData(mission_id=129, task_id=105, name="Class 2 Race Side Mission (Computer by Stadium)",
                             rule=lambda state, player:
                             slums_to_stadium(state, player)),
    130: Jak2SideMissionData(mission_id=130, task_id=106, name="Class 1 Race Side Mission (Computer by Stadium)",
                             rule=lambda state, player:
                             slums_to_stadium(state, player)),
    131: Jak2SideMissionData(mission_id=131, task_id=107, name="Class 3R Race Side Mission (Computer by Stadium)",
                             rule=lambda state, player:
                             slums_to_stadium(state, player)),
    132: Jak2SideMissionData(mission_id=132, task_id=108, name="Class 2R Race Side Mission (Computer by Stadium)",
                             rule=lambda state, player:
                             slums_to_stadium(state, player)),
    133: Jak2SideMissionData(mission_id=133, task_id=109, name="Class 1R Race Side Mission (Computer by Stadium)",
                             rule=lambda state, player:
                             slums_to_stadium(state, player))
}


side_tasks_to_missions = {miss.task_id: miss for _, miss in side_mission_table.items()}
