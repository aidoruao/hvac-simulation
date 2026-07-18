#!/usr/bin/env python3
"""
Generates GDScript locale file from JSON translation.
Usage: python3 locale_generator.py es
Output: godot_project/scripts/locale_es.gd
"""

import json
import sys
import os

def generate_gdscript_locale(lang: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "locales", f"{lang}.json")
    if not os.path.exists(path):
        print(f"FAIL: Locale file not found: {path}")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    godot_data = data.get("godot", {})

    lines = [
        "## Auto-generated from locales/{}.json".format(lang),
        "## Do not edit manually -- run: python3 locale_generator.py {}".format(lang),
        "",
        "const LOCALE_{} = {{".format(lang.upper()),
    ]

    def _dict_to_gdscript(d, indent=1):
        parts = []
        for k, v in d.items():
            key = '"{}"'.format(k)
            if isinstance(v, dict):
                parts.append("\t" * indent + "{}: {{".format(key))
                parts.extend(_dict_to_gdscript(v, indent + 1))
                parts.append("\t" * indent + "},")
            elif isinstance(v, str):
                parts.append("\t" * indent + "{}: \"{}\",".format(key, v.replace('"', '\\"')))
            elif isinstance(v, list):
                items = ', '.join(['"{}"'.format(item.replace('"', '\\"')) for item in v])
                parts.append("\t" * indent + "{}: [{}],".format(key, items))
            else:
                parts.append("\t" * indent + "{}: {},".format(key, json.dumps(v)))
        return parts

    lines.extend(_dict_to_gdscript(godot_data))
    lines.append("}")

    output_path = os.path.join(base_dir, "godot_project", "scripts", f"locale_{lang}.gd")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write((chr(10)).join(lines))

    print(f"Generated: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 locale_generator.py <lang>")
        sys.exit(1)
    generate_gdscript_locale(sys.argv[1])
