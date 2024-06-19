from typing import List
from BaseClasses import CollectionState, MultiWorld
from ..Regions import JakAndDaxterRegion
from ..Rules import can_free_scout_flies, can_trade


def build_regions(level_name: str, player: int, multiworld: MultiWorld) -> List[JakAndDaxterRegion]:

    main_area = JakAndDaxterRegion("Main Area", player, multiworld, level_name, 0)