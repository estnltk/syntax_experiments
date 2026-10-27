from pydantic import BaseModel
from typing import Literal, List, Dict, Union


class ClassificationDict(BaseModel):
    a: Literal["yes", "no"]


class ClassificationAnswer(BaseModel):
    form : dict








