from functools import cache

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from simpatia.config import get_settings
from simpatia.content.loader import load_case_meta, load_locale, load_patient_case
from simpatia.models.case import CaseMeta, PatientCase
from simpatia.models.locale import LocaleConfig

LANGUAGE_NAMES = {"en-GB": "English", "es-ES": "Spanish (Peninsular)"}


@cache
def _env() -> Environment:
    """Jinja environment for prompt templates.

    autoescape is deliberately off: output is plain text sent to an LLM,
    not HTML. Escaping would corrupt apostrophes and accented characters
    in patient dialogue. The separate environment in api/ renders HTML
    and MUST have autoescape enabled.
    """
    return Environment(
        loader=FileSystemLoader(get_settings().content_dir / "prompts"),
        autoescape=False,  # noqa: S701
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )


def render_patient_system(
    case: PatientCase,
    meta: CaseMeta,
    locale: str,
    loc: LocaleConfig,
) -> str:
    template = _env().get_template(f"{locale}/patient_system.jinja")
    return template.render(
        case=case,
        meta=meta,
        background=case.background.model_dump(),
        language_name=loc.language_name,
        max_sentences=loc.max_sentences,
        max_sentences_open=loc.max_sentences_open,
    )


def build_for(case_id: str, locale: str) -> str:
    """Convenience: load and render in one call."""
    return render_patient_system(
        case=load_patient_case(case_id, locale),
        meta=load_case_meta(case_id),
        locale=locale,
        loc=load_locale(locale),
    )
