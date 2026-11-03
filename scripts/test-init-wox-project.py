import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class InitProjectTest(unittest.TestCase):
    def test_reinitialization_updates_package_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / "scripts").mkdir()
            for name in ("plugin.json", "Makefile", "README.md"):
                shutil.copy(ROOT / name, project / name)
            script = project / "scripts/init-wox-project.py"
            shutil.copy(ROOT / "scripts/init-wox-project.py", script)

            manifest_path = project / "plugin.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest.update(Id="test-id", Name="First Plugin", Description="Description", TriggerKeywords=["first"])
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            subprocess.run([sys.executable, str(script), "--apply-existing"], check=True)
            self.assertIn("PLUGIN_NAME := first-plugin", (project / "Makefile").read_text())

            subprocess.run([sys.executable, str(script)], input="Second Plugin\n\n\n\n\ny\n", text=True, check=True)
            self.assertIn("PLUGIN_NAME := second-plugin", (project / "Makefile").read_text())
            self.assertEqual(json.loads(manifest_path.read_text(encoding="utf-8"))["Name"], "Second Plugin")
            self.assertIn("# Second Plugin", (project / "README.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
