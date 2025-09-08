from BaseClasses import Location
from .game_id import jak2_name
from .locs import (mission_locations as missions)


class JakIILocation(Location):
    game: str = jak2_name


all_locations_table = {
    **{k: v for k, v in missions.main_mission_table.items()},
    **{k: v for k, v in missions.side_mission_table.items()}
}
