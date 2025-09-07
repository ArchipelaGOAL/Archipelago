# Archipelago Imports
import settings
from worlds.AutoWorld import World, WebWorld
from worlds.LauncherComponents import components, Component, launch_subprocess, Type, icon_paths
from BaseClasses import (Tutorial, ItemClassification as ItemClass)
from typing import cast, ClassVar
import typing

# Jak 2 imports
from .game_id import jak2_name, jak2_max
from .items import (item_table, 
                    ITEM_ID_KEY_START, ITEM_ID_KEY_END, ITEM_ID_FILLER_START, ITEM_ID_FILLER_END,
                    Jak2ItemData, Jak2Item)
from .locs import (mission_locations)
from .locations import (JakIILocation, all_locations_table)
from .locs.mission_locations import Jak2MissionData
from .regs.region_base import JakIIRegion


def launch_client():
    from . import client
    launch_subprocess(client.launch, name="Jak2Client")


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

    # Settings will be applied after class definition

    web = JakIIWebWorld()

    item_name_to_id = {item_data.name: k for k, item_data in item_table.items()}
    location_name_to_id = {data.name: k for k, data in all_locations_table.items()}
    item_name_groups = {}
    location_name_groups = {}
    origin_region_name = "Mission Tree"

    @staticmethod
    def item_data_helper(item: int) -> list[tuple[int, ItemClass, int]]:
        # count,num,classification
        data: list[tuple[int, ItemClass, int]] = []

        # Determine item classification based on ID ranges
        if ITEM_ID_KEY_START <= item <= ITEM_ID_KEY_END:
            # Key/progression items (IDs 1-33)
            data.append((1, ItemClass.progression | ItemClass.useful, 0))
        elif ITEM_ID_FILLER_START <= item <= ITEM_ID_FILLER_END:
            # Filler items (ID 34+ or high-range jak2_max-10 to jak2_max)
            data.append((1, ItemClass.filler, 0))
        else:
            # If we try to make items with ID's outside defined ranges, something has gone wrong
            raise KeyError(f"Tried to fill item pool with unknown ID {item}. Valid ranges: "
                         f"key items ({ITEM_ID_KEY_START}-{ITEM_ID_KEY_END}), "
                         f"filler items ({ITEM_ID_FILLER_START}-{ITEM_ID_FILLER_END})")
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
            mission_tree_region.add_jak_mission(mission_id, mission.name, mission.rule)

        self.multiworld.regions.append(mission_tree_region)


components.append(Component("Jak II Client",
                            func=launch_client,
                            component_type=Type.CLIENT,
                            icon="jak2_icon"))

# TODO: Add proper icon for Jak 2
icon_paths["jak2_icon"] = f"ap:{__name__}/icons/jak2_icon.png"


class Jak2Settings(settings.Group):
    class RootDirectory(settings.UserFolderPath):
        """Path to folder containing the ArchipelaGOAL Jak 2 mod executables (gk.exe and goalc.exe).
        Ensure this path contains forward slashes (/) only. This setting only applies if
        Auto Detect Root Directory is set to false."""
        description = "ArchipelaGOAL Jak 2 Root Directory"

    class AutoDetectRootDirectory(settings.Bool):
        """Attempt to find the OpenGOAL installation and the Jak 2 mod executables (gk.exe and goalc.exe)
        automatically. If set to true, the ArchipelaGOAL Jak 2 Root Directory setting is ignored."""
        description = "ArchipelaGOAL Jak 2 Auto Detect Root Directory"

    root_directory: RootDirectory = "C:/Program Files/OpenGOAL/features/jak2/mods/archipelagoal/archipelagoal"
    auto_detect_root_directory: AutoDetectRootDirectory = True


# Settings support can be added later once the basic integration works
