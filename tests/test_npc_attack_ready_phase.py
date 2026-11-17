import unittest
from types import SimpleNamespace

import ase_viewer


class NpcAttackReadyPhaseTests(unittest.TestCase):
    def test_phase_classifier_blocks_preparation_and_recovery_variants(self):
        blocked = [
            "Attack_Ready", "Ready_Attack", "ComboAttack_1_Ready",
            "ComboAttackReady", "Attack_Intro", "Attack_Recover",
            "Attack-Windup", "AttackPrepare", "Attack Outro",
        ]
        self.assertTrue(all(not ase_viewer.is_damage_attack_tag(tag) for tag in blocked))
        self.assertTrue(ase_viewer.is_damage_attack_tag("Attack"))
        self.assertTrue(ase_viewer.is_damage_attack_tag("ComboAttack_1"))
        self.assertTrue(ase_viewer.is_damage_attack_tag("ThrustForward"))

    def test_ready_tag_with_hit_slice_has_no_hitbox_or_damage(self):
        player = SimpleNamespace(
            x=40.0, y=500.0, visible=True, hp=100,
            sources=[SimpleNamespace(
                slices={"Hit": [{"frame": 0, "bounds": {
                    "x": 32, "y": 20, "w": 30, "h": 40,
                }}]},
                orig_w=64, orig_h=64,
            )],
            profiles=[], damage_numbers=[], shake_enabled=False,
            play_sound=lambda name: None,
        )
        npc = SimpleNamespace(
            x=0.0, y=500.0, master=player, facing_right=True,
            npc_attack_facing_right=True, active_tag_info=[0, "Attack_Ready"],
            frame_idx=0, npc_attack_has_hit=False,
        )
        self.assertIsNone(ase_viewer.npc_attack_hitbox(npc))
        self.assertFalse(ase_viewer._apply_npc_attack_hit(npc))
        self.assertEqual(player.hp, 100)

    def test_twisted_soldier_like_mapping_activates_only_thrust_phase(self):
        source = SimpleNamespace(
            tags={"ThrustForward_Ready": (0, 0), "ThrustForward": (1, 1)},
            frames=[{"duration": 1000}, {"duration": 900}],
            slices={}, orig_w=64, orig_h=64,
        )
        profile = SimpleNamespace(
            mappings={"ComboAttack_1": [
                [0, "ThrustForward_Ready"], [0, "ThrustForward"],
            ]},
        )
        player = SimpleNamespace(
            x=40.0, y=500.0, visible=True, hp=100, sources=[source],
            profiles=[], damage_numbers=[], shake_enabled=False,
            play_sound=lambda name: None,
        )
        npc = SimpleNamespace(
            x=0.0, y=500.0, master=player, profile=profile,
            facing_right=True, npc_attack_facing_right=True,
            npc_attack_locked=True, npc_attack_slot="ComboAttack_1",
            active_action_slot="ComboAttack_1",
            active_tag_info=[0, "ThrustForward_Ready"],
            npc_attack_elapsed=0.0, npc_attack_has_hit=False,
            npc_attack_cooldown=0.0,
        )
        ase_viewer._set_npc_attack_timing(npc, "ComboAttack_1")
        self.assertEqual(npc.npc_attack_duration, 1900)
        self.assertEqual(npc.npc_attack_active_start, 1000)
        self.assertEqual(npc.npc_attack_active_end, 1225)

        ase_viewer._update_npc_attack_state(npc, 1000)
        self.assertEqual(player.hp, 100)
        npc.active_tag_info = [0, "ThrustForward"]
        ase_viewer._update_npc_attack_state(npc, 1)
        self.assertEqual(player.hp, 95)

        player.hp = 100
        npc.npc_attack_has_hit = False
        npc.npc_attack_elapsed = 1225.1
        ase_viewer._update_npc_attack_state(npc, 1)
        self.assertEqual(player.hp, 100)

    def test_attack_and_combo_fallback_are_immediate_but_not_late(self):
        for tag_name in ("Attack", "ComboAttack_1"):
            player = SimpleNamespace(
                x=40.0, y=500.0, visible=True, hp=100, sources=[],
                profiles=[], damage_numbers=[], shake_enabled=False,
                play_sound=lambda name: None,
            )
            npc = SimpleNamespace(
                x=0.0, y=500.0, master=player,
                facing_right=True, npc_attack_facing_right=True,
                npc_attack_locked=True, npc_attack_slot="ComboAttack_1",
                active_action_slot="ComboAttack_1",
                active_tag_info=[0, tag_name],
                npc_attack_elapsed=0.0,
                npc_attack_duration=400.0,
                npc_attack_has_hit=False,
                npc_attack_cooldown=0.0,
            )
            ase_viewer._update_npc_attack_state(npc, 1)
            self.assertEqual(player.hp, 95, tag_name)

            player.hp = 100
            npc.npc_attack_has_hit = False
            npc.npc_attack_elapsed = 100.1
            ase_viewer._update_npc_attack_state(npc, 1)
            self.assertEqual(player.hp, 100, tag_name)

    def test_active_window_is_zero_to_twenty_five_percent_with_minimum(self):
        self.assertEqual(ase_viewer.NPC_ATTACK_ACTIVE_START_RATIO, 0.0)
        self.assertEqual(ase_viewer.NPC_ATTACK_ACTIVE_END_RATIO, 0.25)
        npc = SimpleNamespace(master=SimpleNamespace(sources=[]), profile=None)
        self.assertEqual(
            ase_viewer._npc_attack_damage_window_ms(npc, "Attack", 400),
            (0.0, 100.0),
        )
        self.assertEqual(
            ase_viewer._npc_attack_damage_window_ms(npc, "Attack", 100),
            (0.0, 40.0),
        )

    def test_combo_detection_rejects_ready_only_mapping(self):
        profile = SimpleNamespace(mappings={
            "ComboAttack_1": [[0, "ComboAttack_1_Ready"]],
            "ComboAttack_2": [[0, "ComboAttack_2"]],
        })
        self.assertEqual(ase_viewer._detect_npc_combo_actions(profile), [])


if __name__ == "__main__":
    unittest.main()
