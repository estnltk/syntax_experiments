import json 
from pydantic import BaseModel
from typing import Literal, List, Dict, Union


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


def few_shot_dialog_to_text(messages:List[Dict[str, str]]) -> str: 
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


def chunk_data(lst, size=10):
    """Yield successive chunks of size N."""
    for i in range(0, len(lst), size):
        yield lst[i:i + size]









