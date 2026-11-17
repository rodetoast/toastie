import unittest
from types import SimpleNamespace
from unittest import mock

import pygame

import ase_viewer


def recovery_player():
    return SimpleNamespace(
        hp=0, max_hp=125, x=42.0, y=360.0,
        hitstop_timer=90, hitstun_timer=40, hit_cooldown=25,
        is_dead=True, is_down=True,
        active_action_slot="HIT_1", active_tag_info=[0, "Hit"],
        action_queue=[[0, "Hit_(Loop)"]], action_end_frame=9,
        particles=[], popup=None, scene_status_message="",
        key_map={"ATTACK": pygame.K_z},
        ai_list=[object()], prop_list=[object()], partner_list=[object()],
        save_settings=mock.Mock(),
    )


class PlayerHpRecoveryShortcutTests(unittest.TestCase):
    def tearDown(self):
        ase_viewer.set_current_language(ase_viewer.LANG_KO)

    def test_restore_is_local_immediate_and_does_not_save(self):
        player = recovery_player()
        position = (player.x, player.y)
        scene_lists = (player.ai_list, player.prop_list, player.partner_list)
        key_map = dict(player.key_map)

        self.assertTrue(ase_viewer.restore_player_hp(player))

        self.assertEqual(player.hp, player.max_hp)
        self.assertEqual((player.x, player.y), position)
        self.assertEqual((player.ai_list, player.prop_list, player.partner_list), scene_lists)
        self.assertEqual(player.key_map, key_map)
        self.assertEqual(player.hitstop_timer, 0)
        self.assertEqual(player.hitstun_timer, 0)
        self.assertFalse(player.is_dead)
        self.assertFalse(player.is_down)
        self.assertIsNone(player.active_action_slot)
        player.save_settings.assert_not_called()

    def test_shortcut_is_blocked_by_input_binding_or_modal(self):
        player = recovery_player()
        self.assertTrue(ase_viewer.can_use_hp_recovery_shortcut(player))
        self.assertFalse(ase_viewer.can_use_hp_recovery_shortcut(player, "gravity"))
        self.assertFalse(ase_viewer.can_use_hp_recovery_shortcut(player, binding_key="ATTACK"))
        player.popup = {"title": "Confirm"}
        self.assertFalse(ase_viewer.can_use_hp_recovery_shortcut(player))
        self.assertFalse(ase_viewer.can_use_hp_recovery_shortcut(None))

    def test_f9_is_app_only_and_status_is_localized(self):
        player = recovery_player()
        self.assertNotIn(pygame.K_F9, player.key_map.values())
        self.assertIn("F9", {item[0] for item in ase_viewer.app_shortcut_guide_items(player)})
        for language, expected in (("ko", "체력 회복"), ("en", "HP Restored")):
            ase_viewer.set_current_language(language)
            ase_viewer.restore_player_hp(player)
            self.assertEqual(player.scene_status_message, expected)

    def test_missing_player_is_safe(self):
        self.assertFalse(ase_viewer.restore_player_hp(None))


if __name__ == "__main__":
    unittest.main()
