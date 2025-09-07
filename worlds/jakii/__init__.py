# Archipelago Imports
from worlds.AutoWorld import World, WebWorld
from BaseClasses import (Tutorial, ItemClassification as ItemClass)
from typing import cast

# Jak 2 imports
from .game_id import jak2_name
from .items import (key_item_table, Jak2ItemData, Jak2Item)
from .locs import (mission_locations)
from .locations import (JakIILocation, all_locations_table)
from .locs.mission_locations import Jak2MissionData
from .regs.region_base import JakIIRegion


class JakIIWebWorld(WebWorld):
    setup_en = Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up ArchipelaGOAL II (Archipelago on OpenGOAL)",
        "English",
        "setup_en.md",
        "setup/en",
        ["narramoment"]
    )

    tutorials = [setup_en]
    bug_report_page = "https://github.com/narramoment/Archipelago/issues"





class JakIIWorld(World):
    """
    Jak II is an action-adventure game published by Naughty Dog in 2003 for the PlayStation 2.
    Set directly after the events of Jak and Daxter: The Precursor Legacy, Jak, Daxter, Samos
    and Keira have set up the Rift Rider they found at the end of their previous adventure, and
    are ready to see where it leads. However, a strange and hostile species of creatures known as
    Metal Heads suddenly fly through the portal, and in a panic, Daxter activates the machine,
    sending them flying through the open portal. Separated, they find themselves in "glorious" Haven City,
    and Jak is quickly captured. Two years later, Daxter finds Jak locked up in prison,
    and Jak has only one thought on his mind: vengeance.
    """

    game = jak2_name

    web = JakIIWebWorld()

    item_name_to_id = {data.name: k for k, data in key_item_table.items()}
    location_name_to_id = {data.name: k for k, data in all_locations_table.items()}
    item_name_groups = {}
    location_name_groups = {}
    origin_region_name = "Mission Tree"

    @staticmethod
    def item_data_helper(item: int) -> list[tuple[int, ItemClass, int]]:
        data: list[tuple[int, ItemClass, int]] = []

        # if item in range(key_item_table, key_item_table):
        #     data.append((1, ItemClass.progression | ItemClass.useful, 0))
        # else:
        #     raise KeyError(f"Tried to fill pool with unknown ID {item}")
        data.append((1, ItemClass.progression | ItemClass.useful, 0))
        return data

    def create_items(self) -> None:
        items_made: int = 0
        for item_name in self.item_name_to_id:
            item_id = self.item_name_to_id[item_name]

            data = self.item_data_helper(item_id)
            for (count, classification, num) in data:
                self.multiworld.itempool += [Jak2Item(item_name, classification, item_id, self.player)
                                             for _ in range(count)]
                items_made += 1

        all_regions = self.multiworld.get_regions(self.player)
        total_locations = sum(reg.location_count for reg in cast(list[JakIIRegion], all_regions))
        total_filler = total_locations - items_made
        self.multiworld.itempool += [self.create_filler() for _ in range(total_filler)]

    def create_item(self, name: str) -> Jak2Item:
        item_id = self.item_name_to_id[name]

        _, classification, _ = self.item_data_helper(item_id)[0]
        return Jak2Item(name, classification, item_id, self.player)

    def get_filler_item_name(self) -> str:
        return "Dark Eco Pill"

    def create_regions(self) -> None:
        mission_tree_region = JakIIRegion("Mission Tree", self.player, self.multiworld)

        for mission_id in all_locations_table:
            mission = all_locations_table[mission_id]
            breakpoint()
            mission_tree_region.add_jak_mission(mission.mission_id, mission.name, mission.rule)

        self.multiworld.regions.append(mission_tree_region)