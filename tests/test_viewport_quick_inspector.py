import os
import unittest
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer


class FakeSource:
    def __init__(self, name="Actor.aseprite"):
        self.name = name
        self.file_path = name
        self.orig_w = 20
        self.orig_h = 20
        self.frames = [
            {"ox": -10, "oy": -20, "duration": 10},
            {"ox": -10, "oy": -20, "duration": 10},
            {"ox": -10, "oy": -20, "duration": 10},
            {"ox": -10, "oy": -20, "duration": 10},
        ]
        self.tags = {
            "IDLE": (0, 1),
            "Idle_(Loop)": (0, 1),
            "Break1": (0, 1),
            "Dead": (0, 1),
            "Destroyed": (0, 1),
            "ComboAttack_1": (2, 2),
            "ComboAttack_2": (3, 3),
        }
        self.tag_list = list(self.tags)
        self.tag_metadata = {}
        self.slices = {}

    def get_frame(self, frame_index, zoom, facing_right):
        del frame_index, facing_right
        return pygame.Surface((int(20 * zoom), int(20 * zoom)), pygame.SRCALPHA)


def make_player():
    player = ase_viewer.AsepritePlayer(
        project_path=os.path.join(os.getcwd(), "__quick_test_project.json"),
        settings_path=os.path.join(os.getcwd(), "__quick_test_settings.json"),
    )
    source = FakeSource()
    player.sources = [source]
    player.zoom = 1.0
    player.cam_x = player.x = 100
    player.cam_y = player.y = 100
    player.last_draw_camera = (100, 100)
    player.visible = True
    profile = ase_viewer.AseProfile("PLAYER", 0, kind="player")
    profile.mappings = {
        "IDLE": [[0, "IDLE"]],
        "ComboAttack_1": [[0, "ComboAttack_1"]],
        "ComboAttack_2": [[0, "ComboAttack_2"]],
    }
    player.profiles = [profile]
    player.cur_profile_idx = 0
    player.cur_source_idx = 0
    player.active_tag_info = [0, "IDLE"]
    player.frame_idx = 0
    return player


class ViewportQuickInspectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_topmost_pick_matches_player_npc_prop_render_order(self):
        player = make_player()
        npc_profile = ase_viewer.AseProfile("NPC", 0, kind="npc")
        prop_profile = ase_viewer.AseProfile("PROP", 0, kind="prop")
        player.profiles.extend([npc_profile, prop_profile])
        npc = ase_viewer.AseAI(player, npc_profile)
        prop = ase_viewer.AseAI(player, prop_profile, is_prop=True)
        for actor in (npc, prop):
            actor.x = player.x
            actor.y = player.y
        player.ai_list = [npc]
        player.prop_list = [prop]
        rect = ase_viewer.actor_visual_screen_rect(player, prop, 640, 570)
        self.assertIs(ase_viewer.viewport_actor_at(player, rect.center, 640, 570), prop)

    def test_left_click_selects_without_opening_and_right_click_opens(self):
        player = make_player()
        point = ase_viewer.actor_visual_screen_rect(player, player, 640, 570).center
        left = ase_viewer.begin_viewport_object_drag(player, player, point, 640, 570)
        self.assertEqual(
            ase_viewer.finish_viewport_left_input(player, left, point, 640, 570),
            "select",
        )
        self.assertIsNone(player.quick_inspector)
        right = {"start": point, "last": point, "dragging": False}
        self.assertIsNotNone(
            ase_viewer.finish_viewport_right_input(player, right, point, 640, 570),
        )

    def test_right_drag_does_not_open_inspector(self):
        player = make_player()
        point = ase_viewer.actor_visual_screen_rect(player, player, 640, 570).center
        state = {"start": point, "last": point, "dragging": True}
        self.assertIsNone(
            ase_viewer.finish_viewport_right_input(player, state, point, 640, 570),
        )
        self.assertIsNone(player.quick_inspector)

    def test_object_drag_preserves_grab_offset_and_uses_zoom_camera_conversion(self):
        player = make_player()
        player.zoom = 2.0
        start = ase_viewer.actor_visual_screen_rect(player, player, 640, 570).center
        state = ase_viewer.begin_viewport_object_drag(player, player, start, 640, 570)
        original = (player.x, player.y)
        self.assertFalse(
            ase_viewer.update_viewport_object_drag(
                player, state, (start[0] + 5, start[1]), 640, 570,
            )
        )
        self.assertEqual((player.x, player.y), original)
        self.assertTrue(
            ase_viewer.update_viewport_object_drag(
                player, state, (start[0] + 20, start[1] + 10), 640, 570,
            )
        )
        self.assertAlmostEqual(player.x, original[0] + 10)
        self.assertAlmostEqual(player.y, original[1] + 5)
        self.assertEqual(ase_viewer.finish_viewport_left_input(
            player, state, (start[0] + 20, start[1] + 10), 640, 570,
        ), "drag")

    def test_npc_and_prop_drag_use_the_same_runtime_position_path(self):
        player = make_player()
        npc_profile = ase_viewer.AseProfile("NPC", 0, kind="npc")
        prop_profile = ase_viewer.AseProfile("PROP", 0, kind="prop")
        player.profiles.extend([npc_profile, prop_profile])
        npc = ase_viewer.AseAI(player, npc_profile)
        prop = ase_viewer.AseAI(player, prop_profile, is_prop=True)
        player.ai_list = [npc]
        player.prop_list = [prop]
        for actor in (npc, prop):
            start = ase_viewer.actor_visual_screen_rect(player, actor, 640, 570).center
            original = (actor.x, actor.y)
            state = ase_viewer.begin_viewport_object_drag(
                player, actor, start, 640, 570,
            )
            self.assertTrue(ase_viewer.update_viewport_object_drag(
                player, state, (start[0] + 12, start[1] - 8), 640, 570,
            ))
            self.assertEqual((actor.x, actor.y), (original[0] + 12, original[1] - 8))
            self.assertTrue(ase_viewer.actor_editor_motion_locked(player, actor))
            ase_viewer.end_viewport_object_drag(player, state)
            self.assertFalse(ase_viewer.actor_editor_motion_locked(player, actor))

    def test_panel_is_clamped_and_keeps_runtime_object_identity(self):
        player = make_player()
        state = ase_viewer.open_quick_inspector(player, player, 360, 330)
        self.assertIs(state["target"], player)
        self.assertGreaterEqual(state["rect"].left, 8)
        self.assertLessEqual(state["rect"].right, 352)
        original_rect = state["rect"].copy()
        player.x += 80
        self.assertEqual(player.quick_inspector["rect"], original_rect)
        ase_viewer.close_quick_inspector(player)
        self.assertIsNone(player.quick_inspector)

    def test_forced_combo_preview_does_not_replace_runtime_animation_state(self):
        player = make_player()
        runtime_state = (player.active_tag_info, player.frame_idx, player.active_action_slot)
        self.assertTrue(
            ase_viewer.start_forced_animation_preview(
                player, player, "ComboAttack_1", full_sequence=True,
            )
        )
        self.assertEqual(len(player.forced_animation_sequence), 2)
        ase_viewer.update_forced_animation_preview(player, player, 11)
        self.assertEqual(player.forced_animation_sequence_index, 1)
        self.assertEqual(
            (player.active_tag_info, player.frame_idx, player.active_action_slot),
            runtime_state,
        )
        ase_viewer.stop_forced_animation_preview(player)
        self.assertEqual(
            (player.active_tag_info, player.frame_idx, player.active_action_slot),
            runtime_state,
        )

    def test_loop_tag_once_finishes_and_repeat_ignores_source_loop_metadata(self):
        player = make_player()
        self.assertTrue(ase_viewer.start_forced_animation_preview(
            player, player, "Idle_(Loop)", repeat=False,
        ))
        ase_viewer.update_forced_animation_preview(player, player, 21)
        self.assertFalse(player.forced_animation_active)
        self.assertTrue(ase_viewer.start_forced_animation_preview(
            player, player, "IDLE", repeat=True,
        ))
        ase_viewer.update_forced_animation_preview(player, player, 45)
        self.assertTrue(player.forced_animation_active)
        self.assertEqual(player.forced_animation_sequence_index, 0)

    def test_full_sequence_repeat_restarts_only_after_the_last_segment(self):
        player = make_player()
        self.assertTrue(ase_viewer.start_forced_animation_preview(
            player, player, "ComboAttack_1", full_sequence=True, repeat=True,
        ))
        ase_viewer.update_forced_animation_preview(player, player, 11)
        self.assertEqual(player.forced_animation_sequence_index, 1)
        ase_viewer.update_forced_animation_preview(player, player, 10)
        self.assertEqual(player.forced_animation_sequence_index, 0)
        self.assertTrue(player.forced_animation_active)

    def test_dropdown_scroll_keyboard_and_visible_row_limit(self):
        player = make_player()
        source = player.sources[0]
        source.tags = {f"Tag_{index:02d}": (0, 0) for index in range(25)}
        source.tag_list = list(source.tags)
        state = ase_viewer.open_quick_inspector(player, player, 640, 570)
        state["selected_tag"] = source.tag_list[-1]
        ase_viewer.handle_quick_inspector_action(
            player, {"action": "toggle_tags", "value": None, "enabled": True},
        )
        self.assertEqual(state["dropdown_scroll"], 17)
        controls = ase_viewer.draw_quick_inspector(
            pygame.Surface((1000, 640)), player, 640, 570,
            (ase_viewer.create_ui_font(12), ase_viewer.create_ui_font(14, bold=True)), [],
        )
        self.assertEqual(
            len([control for control in controls if control["action"] == "select_tag"]),
            ase_viewer.QUICK_INSPECTOR_DROPDOWN_ROWS,
        )
        self.assertIsNotNone(state["dropdown_rect"])
        zoom_before = player.zoom
        self.assertTrue(ase_viewer.handle_quick_inspector_wheel(
            player, state["dropdown_rect"].center, 1,
        ))
        self.assertEqual(player.zoom, zoom_before)
        self.assertTrue(state["dropdown_open"])
        self.assertTrue(ase_viewer.quick_inspector_keyboard(state, source.tag_list, pygame.K_HOME))
        self.assertEqual(state["selected_tag"], "Tag_00")
        self.assertEqual(state["dropdown_scroll"], 0)
        ase_viewer.quick_inspector_scroll_dropdown(state, source.tag_list, 999)
        self.assertEqual(state["dropdown_scroll"], 17)
        self.assertTrue(ase_viewer.handle_quick_inspector_wheel(
            player, state["combo_rect"].center, 999,
        ))
        self.assertEqual(state["dropdown_scroll"], 0)
        state["dropdown_open"] = False
        self.assertFalse(ase_viewer.handle_quick_inspector_wheel(
            player, state["combo_rect"].center, -1,
        ))

    def test_open_dropdown_consumes_modern_and_legacy_wheel_before_draw(self):
        player = make_player()
        source = player.sources[0]
        source.tags = {f"Tag_{index:02d}": (0, 0) for index in range(25)}
        source.tag_list = list(source.tags)
        state = ase_viewer.open_quick_inspector(player, player, 640, 570)
        ase_viewer.handle_quick_inspector_action(
            player, {"action": "toggle_tags", "value": None, "enabled": True},
        )
        self.assertIsNone(state["dropdown_rect"])
        zoom_before = player.zoom
        self.assertTrue(ase_viewer.handle_quick_inspector_wheel(
            player, (-100, -100), -3,
        ))
        self.assertEqual(state["dropdown_scroll"], 3)
        self.assertTrue(state["dropdown_open"])
        self.assertEqual(player.zoom, zoom_before)
        self.assertEqual(
            ase_viewer.quick_inspector_wheel_delta(
                pygame.event.Event(pygame.MOUSEWHEEL, {"y": -1}),
            ),
            -1,
        )
        self.assertEqual(
            ase_viewer.quick_inspector_wheel_delta(
                pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 4}),
            ),
            1,
        )

    def test_scrolled_dropdown_click_controls_reference_visible_bottom_tags(self):
        player = make_player()
        source = player.sources[0]
        source.tags = {f"Tag_{index:02d}": (0, 0) for index in range(25)}
        source.tag_list = list(source.tags)
        state = ase_viewer.open_quick_inspector(player, player, 640, 570)
        state["dropdown_open"] = True
        ase_viewer.quick_inspector_scroll_dropdown(state, source.tag_list, 999)
        controls = ase_viewer.draw_quick_inspector(
            pygame.Surface((1000, 640)), player, 640, 570,
            (ase_viewer.create_ui_font(12), ase_viewer.create_ui_font(14, bold=True)), [],
        )
        visible = [item for item in controls if item["action"] == "select_tag"]
        self.assertEqual(visible[0]["value"], "Tag_17")
        self.assertEqual(visible[-1]["value"], "Tag_24")
        ase_viewer.handle_quick_inspector_action(player, visible[-1])
        self.assertEqual(state["selected_tag"], "Tag_24")
        self.assertFalse(state["dropdown_open"])

    def test_player_and_npc_runtime_motion_are_isolated_until_stop(self):
        player = make_player()
        player.grounded = True
        start_player = (player.x, player.y, player.active_tag_info, player.frame_idx)
        self.assertTrue(ase_viewer.start_forced_animation_preview(
            player, player, "IDLE", repeat=True,
        ))

        class Keys:
            def __getitem__(self, key):
                return key == pygame.K_RIGHT

        player.update(Keys(), 500, 5)
        self.assertEqual(
            (player.x, player.y, player.active_tag_info, player.frame_idx),
            start_player,
        )

        npc_profile = ase_viewer.AseProfile("NPC", 0, kind="npc")
        npc_profile.mappings = {"IDLE": [[0, "IDLE"]], "WALK": [[0, "IDLE"]]}
        player.profiles.append(npc_profile)
        npc = ase_viewer.AseAI(player, npc_profile)
        player.ai_list = [npc]
        npc.decision = "WALK_R"
        npc.vx = 4
        npc_state = (npc.x, npc.y, npc.decision, npc.vx)
        self.assertTrue(ase_viewer.start_forced_animation_preview(
            player, npc, "IDLE", repeat=True,
        ))
        npc.update(500, 16.6)
        self.assertEqual((npc.x, npc.y, npc.decision, npc.vx), npc_state)
        ase_viewer.stop_forced_animation_preview(npc)
        npc.update(500, 16.6)
        self.assertNotEqual(npc.x, npc_state[0])

    def test_player_preview_suppresses_gameplay_hit_generation(self):
        player = make_player()
        player.forced_animation_active = True
        before = (len(player.projectiles), len(player.damage_numbers))
        player.check_hits()
        self.assertEqual((len(player.projectiles), len(player.damage_numbers)), before)
        self.assertTrue(ase_viewer.player_preview_blocks_gameplay_key(
            player, player.key_map["ATTACK"],
        ))
        self.assertTrue(ase_viewer.player_preview_blocks_gameplay_key(
            player, pygame.K_RIGHT,
        ))

    def test_npc_preview_suppresses_attack_damage_without_resetting_attack_state(self):
        player = make_player()
        npc_profile = ase_viewer.AseProfile("NPC", 0, kind="npc")
        player.profiles.append(npc_profile)
        npc = ase_viewer.AseAI(player, npc_profile)
        player.ai_list = [npc]
        npc.x, npc.y = player.x + 5, player.y
        npc.npc_attack_has_hit = False
        npc.npc_attack_locked = True
        player.hp = 100
        self.assertTrue(ase_viewer.start_forced_animation_preview(
            player, npc, "IDLE", repeat=True,
        ))
        self.assertFalse(ase_viewer._apply_npc_attack_hit(npc))
        self.assertEqual(player.hp, 100)
        self.assertTrue(npc.npc_attack_locked)

    def test_death_and_destroy_tags_are_visual_only(self):
        player = make_player()
        player.hp = 77
        player.is_dead = False
        self.assertTrue(ase_viewer.start_forced_animation_preview(
            player, player, "Dead", repeat=True,
        ))
        player.update(type("Keys", (), {"__getitem__": lambda self, key: False})(), 500, 5)
        self.assertEqual(player.hp, 77)
        self.assertFalse(player.is_dead)

        prop_profile = ase_viewer.AseProfile("PROP", 0, kind="prop")
        player.profiles.append(prop_profile)
        prop = ase_viewer.AseAI(player, prop_profile, is_prop=True)
        player.prop_list = [prop]
        particle_count = len(player.particles)
        self.assertTrue(ase_viewer.start_forced_animation_preview(
            player, prop, "Destroyed", repeat=True,
        ))
        prop.update(500, 16.6)
        self.assertFalse(prop.is_dead)
        self.assertIn(prop, player.prop_list)
        self.assertEqual(len(player.particles), particle_count)

    def test_stale_target_closes_during_draw(self):
        player = make_player()
        npc_profile = ase_viewer.AseProfile("NPC", 0, kind="npc")
        player.profiles.append(npc_profile)
        npc = ase_viewer.AseAI(player, npc_profile)
        player.ai_list = [npc]
        self.assertIsNotNone(ase_viewer.open_quick_inspector(player, npc, 640, 570))
        player.ai_list.remove(npc)
        controls = ase_viewer.draw_quick_inspector(
            pygame.Surface((1000, 640)), player, 640, 570,
            (ase_viewer.create_ui_font(12), ase_viewer.create_ui_font(14, bold=True)),
            [],
        )
        self.assertEqual(controls, [])
        self.assertIsNone(player.quick_inspector)

    def test_player_controls_offer_reset_without_facing_or_instance_actions(self):
        player = make_player()
        ase_viewer.open_quick_inspector(player, player, 640, 570)
        controls = ase_viewer.draw_quick_inspector(
            pygame.Surface((1000, 640)), player, 640, 570,
            (ase_viewer.create_ui_font(12), ase_viewer.create_ui_font(14, bold=True)),
            [],
        )
        actions = {control["action"] for control in controls}
        self.assertIn("reset_player_position", actions)
        self.assertNotIn("facing", actions)
        self.assertNotIn("spawn_another", actions)
        self.assertNotIn("despawn", actions)
        self.assertNotIn("terminal", actions)

    def test_player_reset_position_uses_spawn_and_preserves_gameplay_state(self):
        player = make_player()
        profile = player.profiles[0]
        source = player.sources[0]
        player.spawn_x, player.spawn_y = 410, 515
        player.x, player.y = 999, 123
        player.vx, player.vy = 8, -4
        player.hp = 73
        player.facing_right = False
        player.active_tag_info = [0, "ComboAttack_1"]
        ase_viewer.open_quick_inspector(player, player, 640, 570)
        ase_viewer.handle_quick_inspector_action(
            player,
            {"action": "reset_player_position", "value": None, "enabled": True},
        )
        self.assertEqual((player.x, player.y, player.vx, player.vy), (410, 515, 0, 0))
        self.assertEqual(player.hp, 73)
        self.assertFalse(player.facing_right)
        self.assertEqual(player.active_tag_info, [0, "ComboAttack_1"])
        self.assertIs(player.profiles[0], profile)
        self.assertIs(player.sources[0], source)

    def test_npc_terminal_action_delegates_to_existing_death_handler(self):
        player = make_player()
        npc_profile = ase_viewer.AseProfile("NPC", 0, kind="npc")
        player.profiles.append(npc_profile)
        npc = player.spawn_npc_profile(1)
        called = []
        player.trigger_npc_death = lambda target: called.append(
            (target, target.forced_animation_active),
        )
        ase_viewer.open_quick_inspector(player, npc, 640, 570)
        ase_viewer.start_forced_animation_preview(player, npc, "IDLE", repeat=True)
        ase_viewer.handle_quick_inspector_action(
            player,
            {"action": "terminal", "value": None, "enabled": True},
        )
        self.assertEqual(called, [(npc, False)])

    def test_details_closes_inspector_and_requests_existing_settings(self):
        player = make_player()
        ase_viewer.open_quick_inspector(player, player, 640, 570)
        navigation = ase_viewer.handle_quick_inspector_action(
            player,
            {"action": "details", "value": None, "enabled": True},
        )
        self.assertEqual(navigation, "player_settings")
        self.assertIsNone(player.quick_inspector)

    def test_header_drag_clamps_and_manual_position_survives_switch_and_reopen(self):
        player = make_player()
        first = ase_viewer.open_quick_inspector(player, player, 640, 570)
        start = (first["rect"].x + 10, first["rect"].y + 10)
        drag = ase_viewer.begin_quick_inspector_drag(player, start)
        self.assertTrue(ase_viewer.update_quick_inspector_drag(
            player, drag, (-500, -500), 640, 570,
        ))
        manual_position = first["rect"].copy()
        self.assertEqual(manual_position.topleft, (8, ase_viewer.TOP_UI_HEIGHT + 8))

        npc_profile = ase_viewer.AseProfile("NPC", 0, kind="npc")
        player.profiles.append(npc_profile)
        npc = player.spawn_npc_profile(1)
        switched = ase_viewer.open_quick_inspector(player, npc, 640, 570)
        self.assertEqual(switched["rect"].topleft, manual_position.topleft)
        self.assertEqual(
            switched["rect"].height,
            ase_viewer.quick_inspector_content_layout("npc")["height"],
        )
        ase_viewer.close_quick_inspector(player)
        reopened = ase_viewer.open_quick_inspector(player, player, 640, 570)
        self.assertEqual(reopened["rect"].topleft, manual_position.topleft)
        self.assertEqual(
            reopened["rect"].height,
            ase_viewer.quick_inspector_content_layout("player")["height"],
        )

    def test_content_height_contains_all_controls_for_each_actor_kind(self):
        player = make_player()
        npc_profile = ase_viewer.AseProfile("NPC", 0, kind="npc")
        prop_profile = ase_viewer.AseProfile("PROP", 0, kind="prop")
        player.profiles.extend([npc_profile, prop_profile])
        npc = player.spawn_npc_profile(1)
        prop = player.spawn_prop_profile(2)
        actors = ((player, "player", 300), (npc, "npc", 336), (prop, "prop", 336))
        for actor, kind, expected_height in actors:
            state = ase_viewer.open_quick_inspector(player, actor, 640, 570)
            controls = ase_viewer.draw_quick_inspector(
                pygame.Surface((1000, 640)), player, 640, 570,
                (ase_viewer.create_ui_font(12), ase_viewer.create_ui_font(14, bold=True)), [],
            )
            self.assertEqual(state["rect"].height, expected_height)
            ordinary = [item for item in controls if item["action"] != "select_tag"]
            self.assertLessEqual(
                max(item["rect"].bottom for item in ordinary),
                state["rect"].bottom - ase_viewer.QUICK_INSPECTOR_BOTTOM_PADDING,
                kind,
            )

    def test_target_switch_and_close_stop_hidden_repeat_preview(self):
        player = make_player()
        npc_profile = ase_viewer.AseProfile("NPC", 0, kind="npc")
        player.profiles.append(npc_profile)
        npc = player.spawn_npc_profile(1)
        ase_viewer.open_quick_inspector(player, player, 640, 570)
        ase_viewer.start_forced_animation_preview(player, player, "IDLE", repeat=True)
        ase_viewer.open_quick_inspector(player, npc, 640, 570)
        self.assertFalse(player.forced_animation_active)
        ase_viewer.start_forced_animation_preview(player, npc, "IDLE", repeat=True)
        ase_viewer.close_quick_inspector(player)
        self.assertFalse(npc.forced_animation_active)

    def test_spawn_and_despawn_actions_use_same_profile_instance(self):
        player = make_player()
        npc_profile = ase_viewer.AseProfile("NPC", 0, kind="npc")
        player.profiles.append(npc_profile)
        npc = player.spawn_npc_profile(1)
        npc.x, npc.y = 200, 250
        ase_viewer.open_quick_inspector(player, npc, 640, 570)
        ase_viewer.handle_quick_inspector_action(
            player,
            {"action": "spawn_another", "value": None, "enabled": True},
        )
        self.assertEqual(len(player.ai_list), 2)
        self.assertIs(player.ai_list[-1].profile, npc_profile)
        self.assertEqual((player.ai_list[-1].x, player.ai_list[-1].y), (250, 250))
        ase_viewer.handle_quick_inspector_action(
            player,
            {"action": "despawn", "value": None, "enabled": True},
        )
        self.assertNotIn(npc, player.ai_list)
        self.assertIsNone(player.quick_inspector)


if __name__ == "__main__":
    unittest.main()
