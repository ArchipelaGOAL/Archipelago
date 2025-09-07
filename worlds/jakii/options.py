from dataclasses import dataclass
from Options import PerGameCommonOptions, StartInventoryPool, Toggle, Choice, Range, DefaultOnToggle, OptionCounter, \
    AssembleOptions

class CompletionCondition(Choice):
    """Set your goal for completion!"""
    display_name = "Completion Condition"
    option_unlock_mar_tomb = 40
    option_defeat_baron_at_palace = 22
    option_defeat_baron_in_tomb = 43
    option_defeat_metal_kor = 65
    default = 65

@dataclass
class JakIIOptions(PerGameCommonOptions):
    jak_2_completion_condition: CompletionCondition
    start_inventory_from_pool: StartInventoryPool