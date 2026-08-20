# scripts/validate_content.py
import sys

from pydantic import ValidationError

from simpatia.config import settings
from simpatia.content.loader import load_case_meta, load_locale, load_patient_case

errors = []

for meta_path in sorted((settings.content_dir / "cases").glob("*/meta.yaml")):
    case_id = meta_path.parent.name
    try:
        meta = load_case_meta(case_id)
    except (ValidationError, FileNotFoundError) as e:
        errors.append(f"{case_id}/meta.yaml — {e}")
        continue

    for locale in meta.available_locales:
        try:
            load_patient_case(case_id, locale)
            print(f"  ok  {case_id} [{locale}]")
        except (ValidationError, FileNotFoundError) as e:
            errors.append(f"{case_id}/{locale}.yaml — {e}")

for path in sorted((settings.content_dir / "locales").glob("*.yaml")):
    try:
        load_locale(path.stem)
        print(f"  ok  locale {path.stem}")
    except ValidationError as e:
        errors.append(f"locales/{path.stem}.yaml — {e}")

if errors:
    print(f"\n{len(errors)} problem(s):\n", file=sys.stderr)
    for e in errors:
        print(f"  ✗ {e}\n", file=sys.stderr)
    sys.exit(1)

print("\nAll content valid.")
