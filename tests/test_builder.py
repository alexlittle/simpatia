# tests/test_builder.py
import pytest

from simpatia.config import get_settings
from simpatia.content.loader import load_case_meta
from simpatia.prompting.builder import build_for


def _all_case_locales():
    cases_dir = get_settings().content_dir / "cases"
    pairs = []
    for meta_path in sorted(cases_dir.glob("*/meta.yaml")):
        case_id = meta_path.parent.name
        for locale in load_case_meta(case_id).available_locales:
            pairs.append((case_id, locale))
    return pairs


@pytest.mark.parametrize(
    "case_id,locale", _all_case_locales(), ids=lambda v: v if isinstance(v, str) else None
)
def test_build_for_every_declared_locale_is_non_trivial(case_id, locale):
    """Guards against a locale's prompt template silently rendering blank/near-empty.

    An empty or missing Jinja template doesn't raise — it just renders to ''.
    Every declared (case, locale) pair must actually produce a usable prompt.
    """
    prompt = build_for(case_id, locale)
    assert len(prompt) > 200, f"{case_id}/{locale} prompt suspiciously short: {prompt!r}"


def test_build_for_includes_case_content():
    from simpatia.content.loader import load_patient_case

    case = load_patient_case("cholecystitis-01", "en-GB")
    prompt = build_for("cholecystitis-01", "en-GB")
    assert case.opening_line in prompt
    assert case.hpi.site in prompt


def test_build_for_es_es_includes_case_content():
    from simpatia.content.loader import load_patient_case

    case = load_patient_case("cholecystitis-01", "es-ES")
    prompt = build_for("cholecystitis-01", "es-ES")
    assert case.opening_line in prompt
    assert case.hpi.site in prompt


def test_build_for_does_not_leak_diagnosis():
    prompt = build_for("cholecystitis-01", "en-GB")
    assert "cholecystitis" not in prompt.lower()
