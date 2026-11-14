from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# Uma serie registrada pelo aluno (carga e repeticoes feitas)
class SerieSchema(BaseModel):
    workout_exercise_id: int = Field(ge=1)
    set_number: int = Field(ge=1)
    reps_done: int = Field(ge=0, le=255)
    load_kg: float = Field(ge=0, le=9999.99)


class SessionCreateSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    workout_id: int = Field(ge=1)
    performed_at: Optional[datetime] = None
    notes: Optional[str] = None
    sets: List[SerieSchema] = []


class SessionUpdateSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    performed_at: Optional[datetime] = None
    notes: Optional[str] = None
