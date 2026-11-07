"""Sync the bundled skills from Wox and apply the template integration."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
skills = ("wox-plugin-creator", "wox-plugin-submit2store")

with tempfile.TemporaryDirectory() as tmp:
    upstream = Path(tmp) / "wox"
    subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
                    "https://github.com/Wox-launcher/Wox.git", str(upstream)], check=True)
    subprocess.run(["git", "-C", str(upstream), "sparse-checkout", "set",
                    *[f".agents/skills/{skill}" for skill in skills]], check=True)
    for skill in skills:
        if not (upstream / ".agents/skills" / skill).is_dir():
            raise SystemExit(f"Upstream skill not found: {skill}")
    subprocess.run([sys.executable, str(root / "scripts/adapt-synced-skill.py")],
                   cwd=upstream, check=True)
    for skill in skills:
        target = root / ".agents/skills" / skill
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(upstream / ".agents/skills" / skill, target)

subprocess.run([sys.executable, str(root / "scripts/test-scaffold.py")], cwd=root, check=True)
