# tests/test_no_diagnosis_leak.py
import pytest
import yaml
from pydantic import ValidationError

from simpatia.content.loader import load_patient_case
from simpatia.models.case import PatientCase


def test_case_loads():
    case = load_patient_case("cholecystitis-01", "en-GB")
    assert case.opening_line
    assert case.if_asked_only


def test_unknown_field_rejected():
    """A stray diagnosis key must fail loudly, not reach the prompt."""
    raw = {
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
        "diagnosis": "acute cholecystitis",
    }
    with pytest.raises(ValidationError):
        PatientCase.model_validate(raw)


def test_no_case_yaml_contains_a_diagnosis_key(tmp_path):
    """Every case file on disk must parse into PatientCase."""
    from simpatia.config import settings

    for path in (settings.content_dir / "cases").glob("*/[a-z][a-z]-*.yaml"):
        PatientCase.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))

def _case_files():
    from simpatia.config import settings
    return sorted((settings.content_dir / "cases").glob("*/[a-z][a-z]-*.yaml"))

@pytest.mark.parametrize("path", _case_files(), ids=lambda p: f"{p.parent.name}/{p.stem}")
def test_case_file_parses(path):
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert raw is not None, "file is empty"
    PatientCase.model_validate(raw)


def test_declared_locales_exist():
    from simpatia.config import settings
    from simpatia.content.loader import load_case_meta

    for meta_path in (settings.content_dir / "cases").glob("*/meta.yaml"):
        case_id = meta_path.parent.name
        meta = load_case_meta(case_id)
        for locale in meta.available_locales:
            assert (meta_path.parent / f"{locale}.yaml").exists(), (
                f"{case_id} declares {locale} but has no {locale}.yaml"
            )
