import json 
from pydantic import BaseModel
import tiktoken
import openai 
from gpt_cost_estimator import CostEstimator
import os
from openai import AzureOpenAI
import configparser
import time
import pydantic
from pydantic import Field
from typing import Literal, List, Dict, Union
from enum import Enum
import outlines
from outlines.models.openai import OpenAI, OpenAIConfig
from pydantic import ValidationError


def in2json(input_dict:List[Dict[str, str]]):
    """Input dict/json to string using json.dumps.
    """
    return json.dumps(input_dict, ensure_ascii=False)


def user_message(**kwargs) -> Dict[str, Union[str, Dict[str, str]]]:
    """Creates user message with role:user and content from keyword arguments."""
    return {
        "role": "user",
        "content": kwargs
    }


def assistant_message(**kwargs) -> Dict[str, Union[str, Dict[str, str]]]:
    """Creates assistant message with role:assistant and content is yes/no, short answer and long answer.
    """
    mes = {
            "role": "assistant",
            "content": kwargs
            }
    return mes


def messages_2_str(messages:List[Dict[str, str]]):
    """Creates few-shot examples as one string. Makes 5-row blocks of sentence, phrase, yes/no answer, short answer, long answer.
    """
    # kui tahta samad dict prompti asjad anda ette lihtsalt stringina
    # tekitab 5-realised blokid, eraldatud: \n\n
    
    new_string = ""
    
    for mes in messages:
        if mes["role"]=="user":
            l = mes["content"]["l"]
            c = mes["content"]["c"]
            new_string += f"l: {l}\n"
            new_string += f"c: {c}\n"
        if mes["role"]=="assistant":
            if "a" in mes["content"].keys():
                a = mes["content"]["a"]
                new_string += f"a: {a}\n"
            if "s" in mes["content"].keys():
                s = mes["content"]["s"]
                new_string += f"s: {s}\n"
            if "r" in mes["content"].keys():
                r = mes["content"]["r"]
                new_string += f"r: {r}\n\n"
    
    return new_string


def chunks(lst, size=10):
    """Yield successive chunks of size N."""
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


class ClassificationDict(BaseModel):
    a: Literal["yes", "no"]
    #results: List[Literal["yes", "no"]]


class ClassificationAnswer(BaseModel):
    form : dict








