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


def user_message(text:str, phrase:str) -> Dict[str, Union[str, Dict[str, str]]]:
    """Creates user message with role:user and content is input sentence and phrase.
    """
    mes ={
            "role": "user",
            "content": {"l": text, "c": phrase}
            }
    return mes


def assistant_message(yesno:str, short_ans:str, long_ans:str) -> Dict[str, Union[str, Dict[str, str]]]:
    """Creates assistant message with role:assistant and content is yes/no, short answer and long answer.
    """
    mes = {
            "role": "assistant",
            "content": {"a": yesno, "s": short_ans, "r": long_ans}
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
            a = mes["content"]["a"]
            s = mes["content"]["s"]
            r = mes["content"]["r"]
            new_string += f"a: {a}\n"
            new_string += f"s: {s}\n"
            new_string += f"r: {r}\n\n"
    
    return new_string


def classify_batch(my_batch, few_shots, system_prompt, client, deployment):
    """Gets a yes/no answer for a batch of sentences and phrases. 
    """
    #print("classify", len(my_batch))
    max_att = 1
    attempt = 0
    while attempt < max_att:
        attempt += 1
        user_payload = {
            "few_shots": few_shots,
            "batch": my_batch
        }
    
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": in2json(user_payload)}
        ]

        #return None, None
        response = client.chat.completions.create(
            model=deployment,
            messages=messages,
            temperature=0, # absoluutselt min väljund 
        )

        raw_output = response.choices[0].message.content.strip()

        try:
            data = json.loads(raw_output)

            if len(data) != len(batch):
                raise ValueError(f"Väljundis ei ole õige arv vastuseid. Peaks olema {len(batch)} aga on {len(data)}.")
                
            elif len(data) == len(batch):
                for item in data:
                    ClassificationDict(**item)

            return response, raw_output

        except (ValidationError, json.JSONDecodeError, ValueError) as e:
            #print(f"Attempt {attempt} failed. Retrying batch...")
            print(f"Error: {e}")
            #print(f"Raw output: {raw_output[:500]}...")  # preview first 500 chars
            time.sleep(1)  # small delay before retry

    print(f"Batch failed after {max_att} attempts.")
    # isegi kui ei saanud kõike kätte siis saab pärast äkki käsitsi midagi juurde panna
    return response, raw_output


def explain_non_locations(
    client, 
    deployment,
    batch: List[Dict[str, str]],
    yes_no_results: List[str],
    yes_subset_ratio: float = 0.0,

) -> Dict[int, str]:

    # Determine which indices to explain
    no_indices = [i for i, r in enumerate(yes_no_results) if r["a"] == "no"]
    yes_indices = [i for i, r in enumerate(yes_no_results) if r["a"] == "yes"]

    # Diagnostic subset
    diag_count = int(len(yes_indices) * yes_subset_ratio)
    diag_indices = yes_indices[:diag_count]

    explain_indices = no_indices + diag_indices
    if not explain_indices:
        return None, None, None

    items_to_explain = [
        {
            "index": i,
            "l": json.loads(batch[i])["l"],
            "c": json.loads(batch[i])["c"],
            "classification": yes_no_results[i]
        }
        for i in explain_indices
    ]

    messages = [
        {"role": "system", 
         "content": ("Explain why each phrase 'c' was classified as adverbial of place ('yes') or not adverbial of place ('no') in sentence 'l'." 
                       "Give one sentence answer."
                        "You MUST return only a pure JSON object, without markdown and code fences. "
                        "The output must be a mapping: {index: explanation}. "
                        "Do not include ```json or any backticks. Do not include commentary.")
        },
        {"role": "user", "content": (
            """For EACH item without missing any, return a JSON object mapping index → explanation in this format '{"0": "explanation", "3": "explanation"}'.\n"""
            "Items:\n" + in2json(items_to_explain)
        )}
    ]
    #return None, None,None 
    response = client.chat.completions.create(
        model=deployment,
        messages=messages,
    )

    raw = response.choices[0].message.content.strip()

    # ---- Pydantic validation ----
    try:
        ClassificationAnswer(form = json.loads(raw))
    except ValidationError as e:
        raise ValueError(f"Invalid JSON structure returned in explanations:\n{e}")

    return response, raw, explain_indices


def chunks(lst, size=10):
    """Yield successive chunks of size N."""
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


class ClassificationDict(BaseModel):
    a: Literal["yes", "no"]
    #results: List[Literal["yes", "no"]]


class ClassificationAnswer(BaseModel):
    form : dict








