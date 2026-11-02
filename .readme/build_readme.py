#!/usr/bin/env python3
"""Render a GitHub profile README from JSON data and a Jinja2 template."""
from __future__ import annotations

import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / ".readme"


def build() -> str:
    with (SOURCE / "data.json").open(encoding="utf-8") as stream:
        data = json.load(stream)
    environment = Environment(
        loader=FileSystemLoader(str(SOURCE)),
        autoescape=False,  # Markdown output, not HTML.
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )
    template = environment.get_template("README.md.j2")
    rendered = template.render(**data)
    if not rendered.strip():
        raise ValueError("The generated README is empty")
    (ROOT / "README.md").write_text(rendered, encoding="utf-8")
    return rendered


if __name__ == "__main__":
    build()
    print("README.md generated successfully")
