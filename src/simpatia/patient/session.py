"""One consultation between a student and a simulated patient.

Framework-free by design: no FastAPI, no HTTP. The web layer and the
eval runner both drive this same class.
"""

from dataclasses import dataclass, field

from simpatia.content.loader import load_case_meta, load_locale, load_patient_case
from simpatia.llm.client import Message, get_client
from simpatia.prompting.builder import render_patient_system


@dataclass
class Session:
    case_id: str
    locale: str
    system: str
    opening_line: str
    messages: list[Message] = field(default_factory=list)

    @classmethod
    def start(cls, case_id: str, locale: str) -> "Session":
        case = load_patient_case(case_id, locale)
        return cls(
            case_id=case_id,
            locale=locale,
            system=render_patient_system(
                case=case,
                meta=load_case_meta(case_id),
                locale=locale,
                loc=load_locale(locale),
            ),
            opening_line=case.opening_line,
        )

    async def ask(self, utterance: str) -> str:
        self.messages.append({"role": "user", "content": utterance})
        reply = (await get_client("patient").complete(self.system, self.messages)).strip()
        self.messages.append({"role": "assistant", "content": reply})
        return reply

    @property
    def turn_count(self) -> int:
        return len(self.messages) // 2