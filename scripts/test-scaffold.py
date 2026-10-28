from pathlib import Path
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("scaffold", ROOT / ".agents/skills/wox-plugin-creator/scripts/scaffold_wox_plugin.py")
scaffold = importlib.util.module_from_spec(SPEC)
sys.dont_write_bytecode = True
SPEC.loader.exec_module(scaffold)


class ScaffoldTest(unittest.TestCase):
    def test_nodejs_initializes_json_and_project_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "plugin"
            real_run = scaffold.run

            def run(command):
                if command[:2] == ["git", "clone"]:
                    target.mkdir()
                    for name in ("plugin.json", "Makefile", "README.md"):
                        shutil.copy(ROOT / name, target / name)
                    shutil.copytree(ROOT / "scripts", target / "scripts")
                else:
                    real_run(command)

            args = ["scaffold", "--type", "nodejs", "--output-dir", str(target),
                    "--name", "Example Plugin", "--description", 'A "quoted" description',
                    "--trigger-keywords", "one,two", "--author", "Example"]
            with patch.object(sys, "argv", args), patch.object(scaffold, "run", side_effect=run):
                scaffold.main()
            manifest = json.loads((target / "plugin.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["TriggerKeywords"], ["one", "two"])
            self.assertEqual(manifest["Description"], 'A "quoted" description')
            self.assertNotIn("{{", json.dumps(manifest))
            self.assertIn("PLUGIN_NAME := example-plugin", (target / "Makefile").read_text())
            self.assertIn("# Example Plugin", (target / "README.md").read_text())


if __name__ == "__main__":
    unittest.main()
