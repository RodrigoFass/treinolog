from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# Prescricao de um exercicio na ficha (series, reps, carga e descanso)
class PrescricaoSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    exercise_id: int = Field(ge=1)
    sets: int = Field(ge=1, le=20)
    reps: str = Field(min_length=1, max_length=10)
    suggested_load_kg: Optional[float] = Field(default=None, ge=0, le=9999.99)
    rest_seconds: Optional[int] = Field(default=None, ge=0, le=3600)


class WorkoutCreateSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    student_id: int = Field(ge=1)
    name: str = Field(min_length=1, max_length=60)
    notes: Optional[str] = None
    exercises: List[PrescricaoSchema] = []


class WorkoutUpdateSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(default=None, min_length=1, max_length=60)
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class ItemUpdateSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    sets: Optional[int] = Field(default=None, ge=1, le=20)
    reps: Optional[str] = Field(default=None, min_length=1, max_length=10)
    suggested_load_kg: Optional[float] = Field(default=None, ge=0, le=9999.99)
    rest_seconds: Optional[int] = Field(default=None, ge=0, le=3600)
