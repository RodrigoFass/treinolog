from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ExerciseCreateSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=120)
    muscle_group: str = Field(min_length=1, max_length=60)
    description: Optional[str] = None


# Na edicao todos os campos sao opcionais (so altera o que vier no JSON)
class ExerciseUpdateSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    muscle_group: Optional[str] = Field(default=None, min_length=1, max_length=60)
    description: Optional[str] = None
