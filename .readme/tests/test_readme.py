import json
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".readme"))

from build_readme import ProfileData, badge, build, load_data, typing_url


def test_profile_json_validates():
    data = load_data()
    assert data.profile["es"].intro
    assert data.profile["en"].intro


def test_generated_readme_contains_key_sections(tmp_path):
    rendered = build(output=tmp_path / "README.md")
    assert "assets/code.gif" in rendered
    assert "About me" not in rendered
    assert "Java" in rendered and "Kafka" in rendered
    assert "Proyectos destacados" not in rendered
    assert "What I focus on" not in rendered
    assert "## 👨‍💻 Sobre mí" in rendered
    assert (tmp_path / "README.md").read_text(encoding="utf-8") == rendered


def test_rejects_invalid_color():
    data = json.loads((ROOT / ".readme/data.json").read_text(encoding="utf-8"))
    data["technology_groups"][0]["items"][0]["color"] = "invalid"
    with pytest.raises(ValidationError):
        ProfileData.model_validate(data)


def test_rejects_missing_translation():
    data = json.loads((ROOT / ".readme/data.json").read_text(encoding="utf-8"))
    del data["profile"]["en"]
    with pytest.raises(ValidationError):
        ProfileData.model_validate(data)


def test_badge_and_typing_url_encoding():
    tech = load_data().technology_groups[0].items[0]
    assert "img.shields.io/badge/" in badge(tech)
    assert "lines=" in typing_url(["Java & Spring", "Azure"])
    assert "%26" in typing_url(["Java & Spring"])
