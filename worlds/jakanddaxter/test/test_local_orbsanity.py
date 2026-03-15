import unittest
from typing import cast

from test.general import setup_multiworld
from worlds.jakanddaxter import JakAndDaxterWorld

from ..items import orb_item_table


class LocalOrbsanityFillTest(unittest.TestCase):
    """Tests for the local_orbsanity_bundle_percent option.
    These tests require a 2-player multiworld since the option has no effect in singleplayer."""

    def test_local_fill_pulls_all_orbs_from_pool(self):
        """With local percent at 100, all orb bundles (filler and progression) should be pulled from the item pool."""
        jak_options = {
            "enable_orbsanity": 2,  # Global
            "global_orbsanity_bundle_size": 16,
            "local_orbsanity_bundle_percent": 100,
        }
        multiworld = setup_multiworld(
            [JakAndDaxterWorld, JakAndDaxterWorld],
            options=[jak_options, jak_options],
        )

        for player in (1, 2):
            world = cast(JakAndDaxterWorld, multiworld.worlds[player])
            bundle_name = world.orb_bundle_item_name

            # No orb bundles should remain in the pool at 100%.
            orbs_in_pool = [item for item in multiworld.itempool if item.player == player and item.name == bundle_name]
            self.assertEqual(0, len(orbs_in_pool), f"Player {player}: orb bundles should not remain in pool at 100%")

            # They should be stored in local_orb_fill_items instead.
            self.assertGreater(
                len(world.local_orb_fill_items), 0, f"Player {player}: local_orb_fill_items should not be empty at 100%"
            )

    def test_local_fill_zero_percent_no_effect(self):
        """With local percent at 0, no items should be pulled from the pool."""
        jak_options = {
            "enable_orbsanity": 2,  # Global
            "global_orbsanity_bundle_size": 16,
            "local_orbsanity_bundle_percent": 0,
        }
        multiworld = setup_multiworld(
            [JakAndDaxterWorld, JakAndDaxterWorld],
            options=[jak_options, jak_options],
        )

        for player in (1, 2):
            world = cast(JakAndDaxterWorld, multiworld.worlds[player])
            self.assertEqual(
                0, len(world.local_orb_fill_items), f"Player {player}: local_orb_fill_items should be empty at 0%"
            )

    def test_local_fill_partial_percent(self):
        """With local percent at 50, roughly half the orb bundles should be pulled."""
        jak_options = {
            "enable_orbsanity": 1,  # Per Level
            "level_orbsanity_bundle_size": 25,
            "local_orbsanity_bundle_percent": 50,
        }
        multiworld = setup_multiworld(
            [JakAndDaxterWorld, JakAndDaxterWorld],
            options=[jak_options, jak_options],
        )

        for player in (1, 2):
            world = cast(JakAndDaxterWorld, multiworld.worlds[player])
            bundle_name = world.orb_bundle_item_name

            local_count = len(world.local_orb_fill_items)
            pool_count = len(
                [item for item in multiworld.itempool if item.player == player and item.name == bundle_name]
            )
            total_orbs = local_count + pool_count

            # At 50%, local_count should be int(total_orbs * 50 / 100).
            expected = int(total_orbs * 50 / 100)
            self.assertEqual(
                expected, local_count, f"Player {player}: expected {expected} local items but got {local_count}"
            )

    def test_local_fill_includes_progression(self):
        """At 100%, both progression and filler orb bundles should be pulled."""
        jak_options = {
            "enable_orbsanity": 2,  # Global
            "global_orbsanity_bundle_size": 16,
            "local_orbsanity_bundle_percent": 100,
            "citizen_orb_trade_amount": 120,  # Force many progression orbs
        }
        multiworld = setup_multiworld(
            [JakAndDaxterWorld, JakAndDaxterWorld],
            options=[jak_options, jak_options],
        )

        for player in (1, 2):
            world = cast(JakAndDaxterWorld, multiworld.worlds[player])
            prog_items = [item for item in world.local_orb_fill_items if item.advancement]
            filler_items = [item for item in world.local_orb_fill_items if not item.advancement]
            self.assertGreater(len(prog_items), 0, f"Player {player}: should have progression orbs in local fill")
            self.assertGreater(len(filler_items), 0, f"Player {player}: should have filler orbs in local fill")

    def test_local_fill_locations_gathered(self):
        """pre_fill should gather orb bundle locations for placement."""
        jak_options = {
            "enable_orbsanity": 2,  # Global
            "global_orbsanity_bundle_size": 16,
            "local_orbsanity_bundle_percent": 95,
        }
        multiworld = setup_multiworld(
            [JakAndDaxterWorld, JakAndDaxterWorld],
            options=[jak_options, jak_options],
        )

        for player in (1, 2):
            world = cast(JakAndDaxterWorld, multiworld.worlds[player])
            if world.local_orb_fill_items:
                self.assertEqual(
                    len(world.local_orb_fill_locations),
                    len(world.local_orb_fill_items),
                    f"Player {player}: location count should match item count",
                )
                # All gathered locations should be orb bundle locations.
                for loc in world.local_orb_fill_locations:
                    self.assertIn("Orb Bundle", loc.name, f"Player {player}: {loc.name} is not an orb bundle location")

    def test_singleplayer_no_effect(self):
        """In singleplayer, local percent should have no effect even if set."""
        jak_options = {
            "enable_orbsanity": 2,  # Global
            "global_orbsanity_bundle_size": 16,
            "local_orbsanity_bundle_percent": 100,
        }
        multiworld = setup_multiworld(
            JakAndDaxterWorld,
            options=jak_options,
        )

        world = cast(JakAndDaxterWorld, multiworld.worlds[1])
        self.assertEqual(0, len(world.local_orb_fill_items), "local_orb_fill_items should be empty in singleplayer")

    def test_orbsanity_off_no_effect(self):
        """With orbsanity off, local percent should have no effect."""
        jak_options = {
            "enable_orbsanity": 0,  # Off
            "local_orbsanity_bundle_percent": 100,
        }
        multiworld = setup_multiworld(
            [JakAndDaxterWorld, JakAndDaxterWorld],
            options=[jak_options, jak_options],
        )

        for player in (1, 2):
            world = cast(JakAndDaxterWorld, multiworld.worlds[player])
            self.assertEqual(
                0,
                len(world.local_orb_fill_items),
                f"Player {player}: local_orb_fill_items should be empty with orbsanity off",
            )
