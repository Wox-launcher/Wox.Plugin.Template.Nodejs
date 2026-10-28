"""Apply this template's Node.js integration after syncing the Wox skill."""
from pathlib import Path

skill = Path('.agents/skills/wox-plugin-creator')
script = skill / 'scripts/scaffold_wox_plugin.py'
text = script.read_text(encoding='utf-8')
old = '        apply_placeholders_in_tree(output_dir, values)\n        print(f"Cloned {args.type} template into {output_dir}")'
new = '''        if args.type == "nodejs":
            manifest_path = output_dir / "plugin.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest.update(Id=plugin_id, Name=args.name, Description=description,
                            Author=author, Website="", TriggerKeywords=trigger_keywords)
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
            run([sys.executable, str(output_dir / "scripts/init-wox-project.py"), "--apply-existing"])
        else:
            apply_placeholders_in_tree(output_dir, values)
        print(f"Cloned {args.type} template into {output_dir}")'''
if old not in text:
    raise SystemExit('Upstream scaffold changed; update the Node.js integration before syncing.')
text = text.replace('import subprocess\n', 'import subprocess\nimport sys\n', 1).replace(old, new, 1)
script.write_text(text, encoding='utf-8')
reference = skill / 'references/scaffold_nodejs.md'
text = reference.read_text(encoding='utf-8')
if 'make publish' not in text:
    raise SystemExit('Upstream Node.js scaffold instructions changed; review before syncing.')
reference.write_text(text.replace('make publish', 'make package'), encoding='utf-8')
