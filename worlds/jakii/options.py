from dataclasses import dataclass
from Options import PerGameCommonOptions, StartInventoryPool, Choice, Range


class CompletionCondition(Choice):
    """Set your goal for completion!"""
    display_name = "Completion Condition"
    option_complete_specific_mission = 1
    option_complete_number_of_missions = 2
    default = 1


class SpecificMissionForCompletion(Choice):
    """Set the specific mission to complete for the "Complete Specific Mission" completion condition."""
    display_name = "Specific Mission for Completion"
    option_unlock_mar_tomb = 40
    option_defeat_baron_at_palace = 22
    option_defeat_baron_in_tomb = 43
    option_defeat_metal_kor = 65
    default = 65


class NumberOfMissionsForCompletion(Range):
    """Set the number of missions to complete for the "Complete Number of Missions" completion condition."""
    display_name = "Number of Missions for Completion"
    range_start = 5
    range_end = 98
    default = 65


@dataclass
class JakIIOptions(PerGameCommonOptions):
    jak_2_completion_condition: CompletionCondition
    specific_mission_for_completion: SpecificMissionForCompletion
    number_of_missions_for_completion: NumberOfMissionsForCompletion
    start_inventory_from_pool: StartInventoryPool
