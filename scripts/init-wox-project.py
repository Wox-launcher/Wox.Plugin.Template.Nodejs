from __future__ import annotations

import json
import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAKEFILE_PATH = ROOT / "Makefile"
PLUGIN_JSON_PATH = ROOT / "plugin.json"
README_PATH = ROOT / "README.md"
PLACEHOLDER_PATTERN = re.compile(r"\{\{\.[A-Za-z]+\}\}")


def is_placeholder(value: str) -> bool:
    return bool(PLACEHOLDER_PATTERN.fullmatch(value.strip()))


def clean_default(value: str | None, fallback: str = "") -> str:
    if value is None:
        return fallback
    return fallback if is_placeholder(value) else value.strip()


def get_string_value(plugin_data: dict[str, object], field: str) -> str | None:
    value = plugin_data.get(field)
    return value if isinstance(value, str) else None


def get_trigger_keywords(plugin_data: dict[str, object]) -> list[str]:
    value = plugin_data.get("TriggerKeywords")
    if not isinstance(value, list):
        return []

    keywords: list[str] = []
    for item in value:
        if isinstance(item, str):
            normalized_item = item.strip()
            if normalized_item:
                keywords.append(normalized_item)

    return keywords


def is_initialized(plugin_data: dict[str, object]) -> bool:
    required_string_fields = ["Id", "Name", "Description"]
    for field in required_string_fields:
        value = plugin_data.get(field)
        if not isinstance(value, str) or not value.strip() or is_placeholder(value):
            return False

    trigger_keywords = plugin_data.get("TriggerKeywords")
    if not isinstance(trigger_keywords, list):
        return False

    normalized_keywords = []
    for keyword in trigger_keywords:
        if not isinstance(keyword, str):
            return False
        normalized_keyword = keyword.strip()
        if not normalized_keyword or is_placeholder(normalized_keyword):
            return False
        normalized_keywords.append(normalized_keyword)

    return bool(normalized_keywords)


def load_plugin_data() -> dict[str, object]:
    return json.loads(PLUGIN_JSON_PATH.read_text(encoding="utf-8"))


def check_initialized_command() -> int:
    plugin_data = load_plugin_data()
    if is_initialized(plugin_data):
        return 0

    print("Project is not initialized. Run 'make init' first.", file=sys.stderr)
    return 1


def prompt(label: str, default: str = "", required: bool = False) -> str:
    while True:
        suffix = f" [{default}]" if default else ""
        answer = input(f"{label}{suffix}: ").strip()
        if answer:
            return answer
        if default:
            return default
        if not required:
            return ""
        print("This field is required. Please enter a value.")


def prompt_keywords(defaults: list[str]) -> list[str]:
    default_text = ", ".join(defaults)
    while True:
        raw_value = prompt("Trigger keywords (comma-separated for multiple values)", default_text, required=True)
        keywords = [item.strip() for item in raw_value.split(",") if item.strip()]
        if keywords:
            return keywords
        print("At least one trigger keyword is required.")


def package_name_from_plugin_name(name: str) -> str:
    return name.strip().lower() or "plugin"


def update_readme(name: str) -> None:
    content = README_PATH.read_text(encoding="utf-8")
    content = re.sub(
        r"^> For developer\n\n    Please run `make init` to initialize the project\.\n\n",
        "",
        content,
        count=1,
    )
    content = re.sub(r"^#\s+.*$", f"# {name}", content, count=1, flags=re.MULTILINE)
    content = re.sub(r"(?m)^wpm install .*$", f"wpm install {name}", content, count=1)
    README_PATH.write_text(content, encoding="utf-8")


def update_makefile(package_name: str) -> None:
    content = MAKEFILE_PATH.read_text(encoding="utf-8")
    content = content.replace("{{.Name}}", package_name)
    MAKEFILE_PATH.write_text(content, encoding="utf-8")


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--check-initialized":
        return check_initialized_command()

    plugin_data = load_plugin_data()

    current_name = clean_default(get_string_value(plugin_data, "Name"))
    current_description = clean_default(get_string_value(plugin_data, "Description"))
    current_author = clean_default(get_string_value(plugin_data, "Author"))
    current_website = clean_default(get_string_value(plugin_data, "Website"))
    current_id = clean_default(get_string_value(plugin_data, "Id"), str(uuid.uuid4()))
    current_keywords = [keyword for keyword in get_trigger_keywords(plugin_data) if not is_placeholder(keyword)]

    print("Follow the prompts to initialize the plugin project.")
    print("Press Enter to accept the default value shown in brackets.")
    print()

    name = prompt("Plugin name", current_name, required=True)
    description = prompt("Plugin description", current_description, required=True)
    trigger_keywords = prompt_keywords(current_keywords)
    author = prompt("Author", current_author)
    website = prompt("Project website", current_website)
    plugin_id = current_id
    package_name = package_name_from_plugin_name(name)

    print()
    print("Please confirm the following configuration:")
    print(f"  Name: {name}")
    print(f"  Description: {description}")
    print(f"  TriggerKeywords: {', '.join(trigger_keywords)}")
    print(f"  Author: {author or '(empty)'}")
    print(f"  Website: {website or '(empty)'}")
    print(f"  ID: {plugin_id}")
    print(f"  Package file name: {package_name}")

    confirmation = input("Write these values to the project files? [y/N]: ").strip().lower()
    if confirmation not in {"y", "yes"}:
        print("Initialization cancelled.")
        return 1

    plugin_data["Name"] = name
    plugin_data["Description"] = description
    plugin_data["TriggerKeywords"] = trigger_keywords
    plugin_data["Author"] = author
    plugin_data["Website"] = website
    plugin_data["Id"] = plugin_id

    PLUGIN_JSON_PATH.write_text(json.dumps(plugin_data, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
    update_readme(name)
    update_makefile(package_name)

    print("Initialization complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
