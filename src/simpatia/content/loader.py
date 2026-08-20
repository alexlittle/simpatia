# src/simpatia/content/loader.py
from pathlib import Path

import yaml

from simpatia.config import settings
from simpatia.models.case import CaseMeta, PatientCase
from simpatia.models.locale import LocaleConfig


def _read_yaml(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"No content file at {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_case_meta(case_id: str) -> CaseMeta:
    return CaseMeta.model_validate(
        _read_yaml(settings.content_dir / "cases" / case_id / "meta.yaml")
    )


def load_patient_case(case_id: str, locale: str) -> PatientCase:
    """Load patient-visible case content. Never touches rubric/."""
    return PatientCase.model_validate(
        _read_yaml(settings.content_dir / "cases" / case_id / f"{locale}.yaml")
    )


def load_locale(locale: str) -> LocaleConfig:
    return LocaleConfig.model_validate(
        _read_yaml(settings.content_dir / "locales" / f"{locale}.yaml")
    )
