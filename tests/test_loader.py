# tests/test_loader.py
import pytest
from pydantic import ValidationError

from simpatia.config import Settings
from simpatia.content.loader import load_case_meta, load_locale, load_patient_case
from simpatia.models.case import PatientCase
from simpatia.models.locale import LocaleConfig


def test_load_case_meta():
    meta = load_case_meta("cholecystitis-01")
    assert meta.id == "cholecystitis-01"
    assert meta.available_locales == ["en-GB", "es-ES"]


def test_load_case_meta_missing_case_raises():
    with pytest.raises(FileNotFoundError):
        load_case_meta("no-such-case")


@pytest.mark.parametrize("locale", ["en-GB", "es-ES"])
def test_load_patient_case_known_locales(locale):
    case = load_patient_case("cholecystitis-01", locale)
    assert case.lang == locale
    assert case.opening_line
    assert case.hpi.site


def test_load_patient_case_missing_locale_raises():
    with pytest.raises(FileNotFoundError):
        load_patient_case("cholecystitis-01", "fr-FR")


@pytest.mark.parametrize("locale", ["en-GB", "es-ES"])
def test_load_locale_known_locales(locale):
    loc = load_locale(locale)
    assert loc.language_name
    assert loc.max_words > 0


def test_load_locale_missing_raises():
    with pytest.raises(FileNotFoundError):
        load_locale("fr-FR")


def test_malformed_case_yaml_fails_loudly(tmp_path, monkeypatch):
    """A case file that doesn't match the schema must raise, not load silently."""
    case_dir = tmp_path / "cases" / "broken-case"
    case_dir.mkdir(parents=True)
    (case_dir / "en-GB.yaml").write_text("lang: en-GB\nopening_line: hi\n", encoding="utf-8")

    monkeypatch.setattr(
        "simpatia.content.loader.get_settings", lambda: Settings(content_dir=tmp_path)
    )

    with pytest.raises(ValidationError):
        load_patient_case("broken-case", "en-GB")


def test_missing_case_meta_field_fails_loudly(tmp_path, monkeypatch):
    case_dir = tmp_path / "cases" / "broken-case"
    case_dir.mkdir(parents=True)
    (case_dir / "meta.yaml").write_text("id: broken-case\n", encoding="utf-8")

    monkeypatch.setattr(
        "simpatia.content.loader.get_settings", lambda: Settings(content_dir=tmp_path)
    )

    with pytest.raises(ValidationError):
        load_case_meta("broken-case")


def test_patient_case_model_rejects_extra_fields():
    with pytest.raises(ValidationError):
        PatientCase.model_validate(
            {
                "lang": "en-GB",
                "opening_line": "x",
                "hpi": {
                    "site": "x",
                    "onset": "x",
                    "character": "x",
                    "timing": "x",
                    "severity": "x",
                },
                "ice": {"ideas": "x", "concerns": "x", "expectations": "x"},
                "unexpected_field": "should not be allowed",
            }
        )


def test_locale_config_rejects_extra_fields():
    with pytest.raises(ValidationError):
        LocaleConfig.model_validate({"language_name": "English", "max_words": 45, "bogus": True})
