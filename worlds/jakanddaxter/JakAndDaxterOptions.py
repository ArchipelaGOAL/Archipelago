from dataclasses import dataclass
from Options import Toggle, PerGameCommonOptions, Choice


class EnableMoveRandomizer(Toggle):
    """Enable to include movement options as items in the randomizer.
    Jak is only able to run, swim, and single jump, until you find his other moves.
    This adds 11 items to the pool."""
    display_name = "Enable Move Randomizer"


class EnableOrbsanity(Choice):
    """Enable to include bundles of Precursor Orb as an ordered list of progressive checks.
    Every time you collect the chosen number of orbs, you will trigger the next release in the list.

    This adds a number of Items and Locations to the pool inversely proportional to the size of the bundle.
    For example, if your bundle size is 20 orbs, you will add 100 items to the pool. If your bundle size is 250 orbs,
    you will add 8 items to the pool. There are 2000 orbs in the game, so your bundle size must be a factor of 2000."""
    display_name = "Enable Orbsanity"
    option_off = 0
    option_1_orb = 1
    option_2_orbs = 2
    option_4_orbs = 4
    option_5_orbs = 5
    option_8_orbs = 8
    option_10_orbs = 10
    option_16_orbs = 16
    option_20_orbs = 20
    option_25_orbs = 25
    option_40_orbs = 40
    option_50_orbs = 50
    option_80_orbs = 80
    option_100_orbs = 100
    option_125_orbs = 125
    option_200_orbs = 200
    option_250_orbs = 250
    option_400_orbs = 400
    option_500_orbs = 500
    option_1000_orbs = 1000
    option_2000_orbs = 2000
    default = 0


@dataclass
class JakAndDaxterOptions(PerGameCommonOptions):
    enable_move_randomizer: EnableMoveRandomizer
    enable_orbsanity: EnableOrbsanity
