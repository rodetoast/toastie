import unittest
from unittest import mock

import ase_viewer


class WindowIconRuntimeTests(unittest.TestCase):
    def test_source_icon_resolves(self):
        self.assertTrue(ase_viewer.runtime_icon_path().endswith("Icon.png"))

    def test_runtime_setter_calls_pygame_and_missing_is_safe(self):
        icon = mock.Mock()
        icon.get_width.return_value = 32
        icon.get_height.return_value = 32
        with (
            mock.patch.object(ase_viewer, "runtime_icon_path", return_value="Icon.png"),
            mock.patch.object(ase_viewer.pygame.image, "load", return_value=icon) as load,
            mock.patch.object(ase_viewer.pygame.display, "set_icon") as set_icon,
        ):
            self.assertTrue(ase_viewer.set_runtime_window_icon())
            load.assert_called_once_with("Icon.png")
            set_icon.assert_called_once_with(icon)
        with mock.patch.object(ase_viewer, "runtime_icon_path", return_value=None):
            self.assertFalse(ase_viewer.set_runtime_window_icon())

    def test_app_user_model_id_is_safe_off_windows(self):
        with mock.patch.object(ase_viewer.os, "name", "posix"):
            self.assertFalse(ase_viewer.set_windows_app_user_model_id())

    def test_check_message_reports_runtime_icon(self):
        message = ase_viewer.application_check_success_message(
            9, 9, runtime_icon_available=True,
        )
        self.assertIn("runtime_icon=available", message)


if __name__ == "__main__":
    unittest.main()
