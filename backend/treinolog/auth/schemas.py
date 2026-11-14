from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# Schemas de validacao (Pydantic) dos formularios de cadastro, login e vinculo


class RegisterSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=120)
    email: str = Field(min_length=3, max_length=160, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=6, max_length=128)
    role: Literal["personal", "aluno"]


class LoginSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: str = Field(min_length=1, max_length=160)
    password: str = Field(min_length=1, max_length=128)


class LinkSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    invite_code: str = Field(min_length=1, max_length=8)
