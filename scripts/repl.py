"""Interactive terminal client.

    uv run python scripts/repl.py cholecystitis-01 en-GB

Commands: /end  /prompt  /turns  /help
"""

import asyncio
import sys

from simpatia.config import get_settings
from simpatia.patient.session import Session
from simpatia.i18n import t



COMMANDS = ["end", "prompt", "turns", "help"]

def _help(locale: str) -> str:
    lines = [f"  /{c:<8} {t(f'cmd.{c}', locale)}" for c in COMMANDS]
    return "\n" + "\n".join(lines) + "\n"


def handle_command(cmd: str, session: Session, locale: str) -> bool:
    """Return True to keep going, False to end the session."""
    match cmd:
        case "/end":
            return False
        case "/prompt":
            print(f"\n{session.system}\n")
        case "/turns":
            print(f"\n  {t('repl.turn', locale, n=session.turn_count)}\n")
        case "/help":
            print(_help(locale))
        case _:
            print(f"\n  {t('repl.unknown_command', locale, cmd=cmd)}\n")
    return True


async def main(case_id: str, locale: str) -> None:
    session = Session.start(case_id, locale)
    doctor = t("role.doctor", locale)
    patient = t("role.patient", locale)

    print(f"\n  [{get_settings().patient.model} | {case_id} | {locale} | {t('repl.commands_hint', locale)}]")
    print(f"\n  {patient}: {session.opening_line}\n")

    while True:
        try:
            entry = input(f"  {doctor}: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not entry:
            continue
        if entry.startswith("/"):
            if not handle_command(entry, session, locale):
                break
            continue

        reply = await session.ask(entry)
        print(f"\n  {patient}: {reply}")
        print(f"  [{t('repl.words', locale, n=len(reply.split()))}, "
              f"{t('repl.turn', locale, n=session.turn_count)}]\n")

    print(f"\n  {t('repl.ended', locale, turns=session.turn_count)}\n")


if __name__ == "__main__":
    asyncio.run(
        main(
            sys.argv[1] if len(sys.argv) > 1 else "cholecystitis-01",
            sys.argv[2] if len(sys.argv) > 2 else "en-GB",
        )
    )