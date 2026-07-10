#!/usr/bin/env python3
"""Build README.md from JSON data and a Jinja2 Markdown template."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote, quote_plus

import markdown
from jinja2 import (
    Environment,
    FileSystemLoader,
    StrictUndefined,
    TemplateError,
    select_autoescape,
)

ROOT = Path(__file__).resolve().parents[1]
README_DIR = ROOT / ".readme"
DATA_PATH = README_DIR / "data.json"
TEMPLATE_NAME = "README.md.j2"
OUTPUT_PATH = ROOT / "README.md"

SHIELDS_BADGE_STYLE = "for-the-badge"
DEFAULT_BADGE_COLOR = "555555"


class BuildError(Exception):
    """Raised when the README cannot be generated from the given inputs."""


def md_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def _badge_label(text: str) -> str:
    # shields.io uses "-" as a field separator and "_"/"--" as escapes for
    # literal spaces/hyphens in a label; anything else must be percent-encoded.
    escaped = text.replace("-", "--").replace(" ", "_")
    return quote(escaped, safe="_-")


def _shields_badge_url(label: str, color: str, logo: str | None, logo_color: str = "white") -> str:
    url = f"https://img.shields.io/badge/{_badge_label(label)}-{color}?style={SHIELDS_BADGE_STYLE}"
    if logo:
        url += f"&logo={logo}&logoColor={logo_color}"
    return url


def md_badges(items: list[dict[str, Any]]) -> str:
    """Render shields.io/simple-icons badges for a list of {name, color, logo, logo_color} items."""
    badges = (
        f"![{item['name']}]({_shields_badge_url(item['name'], item.get('color', DEFAULT_BADGE_COLOR), item.get('logo'), item.get('logo_color', 'white'))})"
        for item in items
    )
    return " ".join(badges)


def md_social_badges(items: list[dict[str, Any]]) -> str:
    """Render clickable shields.io badges for a list of {label, url, color, logo} items.

    Uses raw HTML (not Markdown image/link syntax) so the badges can sit inside an
    `align="center"` block without a blank line — GitHub's Markdown renderer only
    centers content that stays inside the same raw-HTML block as the wrapping tag.
    """
    badges = (
        f'<a href="{item["url"]}"><img src="{_shields_badge_url(item["label"], item.get("color", DEFAULT_BADGE_COLOR), item.get("logo"))}" alt="{item["label"]}"></a>'
        for item in items
    )
    return " ".join(badges)


def typing_svg_url(config: dict[str, Any]) -> str:
    """Build a readme-typing-svg.demolab.com URL from a typing config block."""
    params = {
        "font": config.get("font", "Fira Code"),
        "weight": config.get("weight", 600),
        "size": config.get("size", 24),
        "duration": config.get("duration", 3000),
        "pause": config.get("pause", 1000),
        "color": config.get("color", "0E75B6"),
        "center": str(config.get("center", True)).lower(),
        "vCenter": str(config.get("v_center", True)).lower(),
        "width": config.get("width", 600),
        "lines": ";".join(config["lines"]),
    }
    if config.get("background"):
        params["background"] = config["background"]

    query = "&".join(f"{key}={quote_plus(str(value))}" for key, value in params.items())
    return f"https://readme-typing-svg.demolab.com?{query}"


def read_data(data_path: Path) -> dict[str, Any]:
    try:
        raw = data_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise BuildError(f"No se encontró el archivo de datos: {data_path}") from exc

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise BuildError(
            f"JSON inválido en {data_path} (línea {exc.lineno}, columna {exc.colno}): {exc.msg}"
        ) from exc


def build_environment(readme_dir: Path) -> Environment:
    env = Environment(
        loader=FileSystemLoader(readme_dir),
        autoescape=select_autoescape(disabled_extensions=("md", "j2")),
        trim_blocks=True,
        lstrip_blocks=True,
        undefined=StrictUndefined,
    )
    env.filters["md_list"] = md_list
    env.filters["md_badges"] = md_badges
    env.filters["md_social_badges"] = md_social_badges
    env.filters["typing_svg_url"] = typing_svg_url
    return env


def render_readme(data: dict[str, Any], readme_dir: Path, template_name: str) -> str:
    try:
        template = build_environment(readme_dir).get_template(template_name)
        content = template.render(**data).rstrip() + "\n"
    except TemplateError as exc:
        raise BuildError(f"Error al renderizar la plantilla '{template_name}': {exc}") from exc

    try:
        # Render once to HTML so malformed Markdown/Jinja output fails early in CI.
        markdown.markdown(content, extensions=["extra"])
    except Exception as exc:  # noqa: BLE001 - surface any markdown parsing failure
        raise BuildError(f"El Markdown generado no es válido: {exc}") from exc

    return content


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA_PATH, help="Ruta al JSON de datos")
    parser.add_argument(
        "--template-dir", type=Path, default=README_DIR, help="Directorio de plantillas Jinja2"
    )
    parser.add_argument("--template", default=TEMPLATE_NAME, help="Nombre del template a usar")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH, help="Ruta de salida del README")
    parser.add_argument(
        "--check",
        action="store_true",
        help="No escribe el archivo; falla si el README generado difiere del existente",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        content = render_readme(read_data(args.data), args.template_dir, args.template)
    except BuildError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1

    if args.check:
        current = args.output.read_text(encoding="utf-8") if args.output.exists() else None
        if current != content:
            print(f"❌ {args.output} está desactualizado respecto a los datos/plantilla.", file=sys.stderr)
            return 1
        print(f"✅ {args.output} está actualizado.")
        return 0

    args.output.write_text(content, encoding="utf-8")
    print(f"✅ README generado en {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
