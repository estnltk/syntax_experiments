import os 
import sys 
import json

from common_code.gpt_utils import *


SYSTEM_PROMPT = """
You are a classification assistant.
Your task: Given a list of JSON objects, each with keys "l" (sentence) and "c" (phrase), classify whether "c" is a location in the context of the sentence.
Locations: names of locations, buildings and bussinesses (bankhouse, studio, club), physical objects and living things, areas that have a defined geographic location, abstract places.
Not locations: actions and events, living beings who are action takers, state of being, ordinance, causal regulation, adverb of time, constructions and stamp expressions.
Output requirements:
- Respond with an array of JSON objects, one per input item.
- The output array must be in the exact same order as the input items.
- The output object must have "yes" (location) or "no" (not location) for each input item
- Do NOT give a longer reason like in few_shots.
Rules:
- Strict JSON only.
- No commentary.
- No markdown.
- No merging of items — one output per input.
"""

FEW_SHOTS = [
            {
            "role": "user",
            "content": in2json({"l": "Me läksime Pariisi", "c": "Pariisi"})
            },
            {
            "role": "assistant",
            "content": in2json({"a": "yes", "s": "city", "r": "Phrase is a city name and therefore location."})
            },

            {
            "role": "user",
            "content": in2json({"l": "Ema on mul olnud alati õmblustöö inimene ja õpetab seda praegu ühes õmbluskoolis teistelegi.", "c": "õmbluskoolis"})
            },
            {
            "role": "assistant",
            "content": in2json({"a": "yes", "s": "building", "r": "Phrase is a buidlding but also a bussiness."})
            },

            {
            "role": "user",
            "content": in2json({"l": "Põhjapoolusele saabus kottide-kompsudega tuhandeid võõrtöölisi.", "c": "Põhjapoolusele"})
            },
            {
            "role": "assistant",
            "content": in2json({"a": "yes", "s": "location", "r": "Phrase is an area with defined geographical location."})
            },

            {
            "role": "user",
            "content": in2json({"l": "Ta tuli idast kõikide oma raamatutega.", "c": "idast"})
            },
            {
            "role": "assistant",
            "content": in2json({"a": "yes", "s": "direction", "r": "Phrase is an area with defined geographical location in the context of this sentence."})
            },

            {
            "role": "user",
            "content": in2json({"l": "Mees istus peale pikka päeva uuesti sadulasse.", "c": "sadulasse"})
            },
            {
            "role": "assistant",
            "content": in2json({"a": "yes", "s": "object", "r": "Phrase is an object that can be defines as location."})
            },
    
            {
            "role": "user",
            "content": in2json({"l": "Ta alustas tööd kell üheksa", "c": "kell üheksa"})
            },
            {
            "role": "assistant",
            "content": in2json({"a": "no", "s": "time", "r": "Phrase is time expression not location."})
            },

            {
            "role": "user",
            "content": in2json({"l": "Avo Mäeseppa süüdistati selles, et ta eelmise aasta sügisel varastas magava J.P. põuetaskust salaja raha koos rahakotiga.", "c": "põuetaskust"})
            },
            {
            "role": "assistant",
            "content": in2json({"a": "no", "s": "abstract", "r": "The theft did not happen in põuetasku and therefore is not a location."})
            },

            {
            "role": "user",
            "content": in2json({"l": "Näiteks korraldas Affleck Lopezile üllatus-sünnipäevapeo restoranis Park.", "c": "restoranis"})
            },
            {
            "role": "assistant",
            "content": in2json({"a": "no", "s": "abstract", "r": "The party is planned to be in a restaurant but the action of planning is not happening there."})
            },

            {
            "role": "user",
            "content": in2json({"l": "HP700 ei ulatu enam SpeedTouchi Wifi'sse.", "c": "Wifi'sse"})
            },
            {
            "role": "assistant",
            "content": in2json({"a": "no", "s": "abstract", "r": "The geographic location of the phrase acn't be determined."})
            },

            {
            "role": "user",
            "content": in2json({"l": "Minnie käis Barbra teadmata isegi kleidiproovis.", "c": "kleidiproovis"})
            },
            {
            "role": "assistant",
            "content": in2json({"a": "no", "s": "event", "r": "Phrase is an event."})
            },

            {
            "role": "user",
            "content": in2json({"l": "Rüselejal käsisid sussid", "c": "Rüselejal"})
            },
            {
            "role": "assistant",
            "content": in2json({"a": "no", "s": "actor", "r": "Phrase refers to action taker."})
            },

            {
            "role": "user",
            "content": in2json({"l": "Nüüd siis istun sitas.", "c": "sitas"})
            },
            {
            "role": "assistant",
            "content": in2json({"a": "no", "s": "state", "r": "Phrase refers to state of being."})
            },

            {
            "role": "user",
            "content": in2json({"l": "Protest on mitmekesine ja teravaimalt avaldub see kirjanduses.", "c": "teravaimalt"})
            },
            {
            "role": "assistant",
            "content": in2json({"a": "no", "s": "ordinance", "r": "Phrase refers to ordinance and is not location."})
            },

            {
            "role": "user",
            "content": in2json({"l": "Tulbisibul on siinkohal platseebo ja selle hävitamisel kaovad ka sümptomid.", "c": "hävitamisel"})
            },
            {
            "role": "assistant",
            "content": in2json({"a": "no", "s": "regulation", "r": "The phrase is causal regulation."})
            },

            {
            "role": "user",
            "content": in2json({"l": "Rahulepingu kehtivusest lähtus omariikluse taastamise käigus Ülemnõukogu.", "c": "kehtivusest"})
            },
            {
            "role": "assistant",
            "content": in2json({"a": "no", "s": "construction", "r": "The phrase refers to construction of stamp expression."})
            },

            {
            "role": "user",
            "content": in2json({"l": "Korraldasime seminari TTÜs.", "c": "TTÜs"})
            },
            {
            "role": "assistant",
            "content": in2json({"a": "no", "s": "org", "r": "The phrase refers to organization."})
            },

            {
            "role": "user",
            "content": in2json({"l": "Väga hästi varjab päikesekiiri näiteks markiis.", "c": "markiis"})
            },
            {
            "role": "assistant",
            "content": in2json({"a": "no", "s": "object", "r": "The phrase refers to an object that is in the inessive case but is not the location of the action."})
            },

            {
            "role": "user",
            "content": in2json({"l": "Ingridi puhul läks hiljem täkkesse just see ütelus.", "c": "täkkesse"})
            },
            {
            "role": "assistant",
            "content": in2json({"a": "no", "s": "stamp", "r": "The phrase is in illativa case but is a stamp expression."})
            },

]
 

