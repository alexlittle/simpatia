# src/simpatia/models/case.py
"""Patient-visible case content.

Deliberately has no diagnosis or mark-scheme field. The examiner's answer key
lives in models/rubric.py and is loaded by a separate function, so the
diagnosis cannot reach the patient's prompt even by accident.
"""

from pydantic import BaseModel, ConfigDict, Field


class CaseMeta(BaseModel):
    """Language-neutral facts. One per case, shared across locales."""

    model_config = ConfigDict(extra="forbid")

    id: str
    presenting_complaint: str
    age: int = Field(ge=0, le=120)
    sex: str
    difficulty: int = Field(ge=1, le=5)
    duration_minutes: int = Field(default=10, ge=1, le=30)
    available_locales: list[str] = Field(min_length=1)


class HPI(BaseModel):
    """History of presenting complaint, in the patient's own words."""

    model_config = ConfigDict(extra="forbid")

    site: str
    onset: str
    character: str
    radiation: str | None = None
    associated: list[str] = []
    timing: str
    exacerbating: str | None = None
    relieving: str | None = None
    severity: str


class ICE(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ideas: str
    concerns: str
    expectations: str


class Background(BaseModel):
    model_config = ConfigDict(extra="forbid")

    past_medical: list[str] = []
    medications: list[str] = []
    allergies: list[str] = []
    family: list[str] = []
    social: list[str] = []


class PatientCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lang: str
    opening_line: str

    hpi: HPI
    background: Background = Background()
    ice: ICE

    # Disclosure control — what makes the encounter discriminate between students
    volunteered_freely: list[str] = []
    if_asked_only: list[str] = []
    denies: list[str] = []
    does_not_know: list[str] = []
