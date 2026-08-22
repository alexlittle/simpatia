"""UI string lookup. Distinct from case content — this is ordinary i18n."""

import json
from functools import cache

from simpatia.config import get_settings


@cache
def _strings(locale: str) -> dict[str, str]:
    path = get_settings().content_dir / "ui" / f"{locale}.json"
    if not path.exists():
        path = get_settings().content_dir / "ui" / f"{get_settings().default_locale}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def t(key: str, locale: str, **kwargs: object) -> str:
    """Translate a key, falling back to the key itself if missing."""
    template = _strings(locale).get(key, key)
    return template.format(**kwargs) if kwargs else template