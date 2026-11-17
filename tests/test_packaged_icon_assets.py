import pathlib
import unittest

from PIL import Image


ROOT = pathlib.Path(__file__).resolve().parents[1]


class PackagedIconAssetsTests(unittest.TestCase):
    def test_executable_and_runtime_icons_are_configured(self):
        spec = (ROOT / "ase_viewer.spec").read_text(encoding="utf-8")
        self.assertIn("icon='Icon.ico'", spec)
        self.assertIn("('Icon.png', '.')", spec)
        self.assertTrue((ROOT / "Icon.ico").is_file())
        self.assertTrue((ROOT / "Icon.png").is_file())

    def test_icon_assets_open_with_alpha_and_required_ico_sizes(self):
        with Image.open(ROOT / "Icon.png") as png:
            self.assertEqual(png.format, "PNG")
            self.assertIn("A", png.getbands())
            self.assertEqual(png.size, (1024, 1024))
        with Image.open(ROOT / "Icon.ico") as ico:
            self.assertEqual(ico.format, "ICO")
            self.assertIn("A", ico.getbands())
            self.assertEqual(
                set(ico.info.get("sizes", [])),
                {(16, 16), (32, 32), (48, 48), (64, 64),
                 (128, 128), (256, 256)},
            )

    def test_icon_sha256_values_are_recordable(self):
        import hashlib

        for name in ("Icon.png", "Icon.ico"):
            digest = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            self.assertEqual(len(digest), 64)
            self.assertTrue(all(char in "0123456789abcdef" for char in digest))


if __name__ == "__main__":
    unittest.main()
