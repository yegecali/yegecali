#!/usr/bin/env python3
"""Build README.md from JSON data and a Jinja2 Markdown template."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import markdown
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape


ROOT = Path(__file__).resolve().parents[1]
README_DIR = ROOT / ".readme"
DATA_PATH = README_DIR / "data.json"
TEMPLATE_NAME = "README.md.j2"
OUTPUT_PATH = ROOT / "README.md"


def inline_code(value: str) -> str:
    return f"`{value}`"


def md_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def md_badges(items: list[str]) -> str:
    return " ".join(inline_code(item) for item in items)


def read_data() -> dict[str, Any]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def build_environment() -> Environment:
    env = Environment(
        loader=FileSystemLoader(README_DIR),
        autoescape=select_autoescape(disabled_extensions=("md", "j2")),
        trim_blocks=True,
        lstrip_blocks=True,
        undefined=StrictUndefined,
    )
    env.filters["md_list"] = md_list
    env.filters["md_badges"] = md_badges
    return env


def render_readme(data: dict[str, Any]) -> str:
    template = build_environment().get_template(TEMPLATE_NAME)
    content = template.render(**data).rstrip() + "\n"

    # Render once to HTML so malformed Markdown/Jinja output fails early in CI.
    markdown.markdown(content, extensions=["extra"])
    return content


def main() -> None:
    OUTPUT_PATH.write_text(render_readme(read_data()), encoding="utf-8")


if __name__ == "__main__":
    main()
