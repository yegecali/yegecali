#!/usr/bin/env python3
"""Validate JSON profile data and render a Spanish GitHub README."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import quote, urlparse

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / ".readme"


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LocalizedProfile(StrictModel):
    headline: str = Field(min_length=10)
    intro: str = Field(min_length=80)
    focus: list[str] = Field(min_length=2)
    approach: list[str] = Field(min_length=2)


class Technology(StrictModel):
    name: str = Field(min_length=1)
    color: str
    logo: str = ""

    @field_validator("color")
    @classmethod
    def hex_color(cls, value: str) -> str:
        if not re.fullmatch(r"[0-9A-Fa-f]{6}", value):
            raise ValueError("color must contain six hexadecimal digits")
        return value


class TechnologyGroup(StrictModel):
    title_es: str
    title_en: str
    items: list[Technology] = Field(min_length=1)


class Link(StrictModel):
    label: str
    url: HttpUrl


class Project(StrictModel):
    name: str
    description: str
    url: HttpUrl


class ProfileData(StrictModel):
    name: str = Field(min_length=2)
    location: str
    locale: str
    profile: dict[str, LocalizedProfile]
    technology_groups: list[TechnologyGroup] = Field(min_length=1)
    typing_lines: list[str] = Field(min_length=1)
    animation_url: HttpUrl
    links: list[Link]
    featured_projects: list[Project]

    @field_validator("profile")
    @classmethod
    def required_languages(cls, value: dict[str, LocalizedProfile]):
        if not {"es", "en"}.issubset(value):
            raise ValueError("Both es and en profiles are required")
        return value

    @field_validator("locale")
    @classmethod
    def supported_locale(cls, value: str):
        if value not in {"es", "en"}:
            raise ValueError("locale must be es or en")
        return value


def badge(technology: Technology) -> str:
    name = quote(technology.name.replace("-", "--").replace("_", "__").replace(" ", "_"), safe="_")
    url = f"https://img.shields.io/badge/{name}-{technology.color}?style=for-the-badge"
    if technology.logo:
        url += f"&logo={quote(technology.logo)}&logoColor=white"
    return f"![{technology.name}]({url})"


def typing_url(lines: list[str]) -> str:
    params = "&".join((
        "font=Fira+Code", "weight=600", "size=22", "duration=3000",
        "pause=1000", "color=0E75B6", "center=true", "vCenter=true", "width=780",
    ))
    return "https://readme-typing-svg.demolab.com?" + params + "&lines=" + quote(";".join(lines), safe=";")


def load_data(path: Path = SOURCE / "data.json") -> ProfileData:
    with path.open(encoding="utf-8") as stream:
        return ProfileData.model_validate(json.load(stream))


def build(output: Path = ROOT / "README.md", data_path: Path = SOURCE / "data.json") -> str:
    data = load_data(data_path)
    environment = Environment(
        loader=FileSystemLoader(str(SOURCE)),
        autoescape=False,
        undefined=StrictUndefined,
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    environment.filters["badge"] = badge
    template = environment.get_template("README.md.j2")
    rendered = template.render(
        data=data, es=data.profile["es"], en=data.profile["en"],
        typing_svg=typing_url(data.typing_lines),
    )
    required = ["assets/code.gif", "## 🧰", "github.com/yegecali"]
    if not all(marker in rendered for marker in required):
        raise ValueError("Generated README is missing required profile sections")
    if not rendered.strip():
        raise ValueError("Generated README is empty")
    output.write_text(rendered, encoding="utf-8")
    return rendered


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Validate without writing README")
    args = parser.parse_args()
    if args.check:
        load_data()
        print("Profile JSON validated")
    else:
        build()
        print("README.md generated successfully")
