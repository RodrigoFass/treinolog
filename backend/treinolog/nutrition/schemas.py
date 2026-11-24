import datetime as dt
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

# Schemas de validacao (Pydantic) dos formularios do nutricionista e do aluno


# Uma refeicao do plano (nome, horario, alimentos e calorias)
class MealSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=60)
    time: Optional[str] = Field(default=None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    foods: str = Field(min_length=1, max_length=1000)
    kcal: Optional[int] = Field(default=None, ge=0, le=5000)


class MealPlanCreateSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    student_id: int = Field(ge=1)
    name: str = Field(min_length=1, max_length=60)
    goal: Optional[str] = Field(default=None, max_length=120)
    notes: Optional[str] = None
    meals: List[MealSchema] = Field(min_length=1, max_length=10)


class MealPlanUpdateSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(default=None, min_length=1, max_length=60)
    goal: Optional[str] = Field(default=None, max_length=120)
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    meals: Optional[List[MealSchema]] = Field(default=None, min_length=1, max_length=10)


class MealCheckSchema(BaseModel):
    day: Optional[dt.date] = None
    done: bool


class WeightSchema(BaseModel):
    day: Optional[dt.date] = None
    weight_kg: float = Field(gt=20, lt=400)
