import os 
import sys 

#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../../common_code")))
from common_code.gpt_utils import *


ALIVE_SYSTEM_PROMPT = """
You are a classification assistant.
Your task: Given a list of examples, each with keys "l" (sentence) and "c" (phrase), classify whether "c" is alive in the context of the sentence.
Criteria for alive:
- living beings (mother, sister, cat)
- occupation (doctor, soldier, teacher, captain)
- names of people (Aita, Ines, Peeter)
- pronouns (he, she, I, me , we, they, who, whom, kes, kellel)
- nationality and ethnic identifier (Estonian, Jew, German, Christian)
- metaphors (kobakäpp, sehkendaja, marakratt)

Analyse the given criteria, analyse the 'few_shots' examples and generalise.
Then process the list called 'batch'.

Output JSON requirements:
- Respond strictly with an array of JSON objects, one object per 'batch' item.
- The JSON array must be in the exact same order as the batch items.
- Response must be without markdown or comments.
- Each output JSON must have:
  "a": "yes" (alive) or "no" (not alive)
"""

ALIVE_FEW_SHOTS = [
            user_message(l="Noorim õdedest viskas kivi.",c="õdedest"),
            assistant_message(a="yes", r="Sister is a living being."),
    
            user_message(l="Juulis Kingseppa külastanud treener oli õnnelik.", c="Kingseppa"),
            assistant_message(a="yes", r="Kingsepp is a name of a person."),
    
            user_message(l="Siis pääses minust karjatus", c="minust"),
            assistant_message(a="yes", r="'from me' refers to living being."),

            user_message(l="Temas on midagi erilist.",c= "Temas"),
            assistant_message(a="yes", r="'Tema' refers to human."),

            user_message(l="Sellisest sehkendajast poleks seda oodanud.", c="sehkendajast"),
            assistant_message(a="yes", r="Metaphor that refers to human."),
    
            user_message(l="Kas üks nendest, kes põgenes?", c="kes"),
            assistant_message(a="yes", r="'kes' refers to human."),
]

ALIVE_FEW_SHOTS_STR = few_shot_dialog_to_text(ALIVE_FEW_SHOTS)



EVENT_SYSTEM_PROMPT = """
You are a classification assistant.
Your task: Given a list of examples, each with keys "l" (sentence) and "c" (phrase), classify if "c" refers to an event in the context of the sentence.
A phrase is an event when:
1. It describes an action, occurrence, or state change.
2. It refers to something that happens.
3. It has both a time (when) and a location (where).
4. Time and place can be inferred based on common sense if not specified in the phrase.

Analyse all criteria, analyse the 'few_shots' examples and generalise.
Then process the list called 'batch' based on the criteria.

Output JSON requirements:
- Respond strictly with an array of JSON objects, one object per 'batch' item.
- The JSON array must be in the exact same order as the batch items.
- Response must be without markdown or comments.
- Each output JSON must have:
  "a": "yes" (event) or "no" (not event)
"""

EVENT_FEW_SHOTS = [
            user_message(l="Näiteks räägitakse nii mõneski koolis osa õpilasi lihtsalt pehmeks , et nad ei roniks teatud eksamile .", c="eksamile"),
            assistant_message(a="yes", r="Exam usually happens at a specific time and location."),
    
            user_message(l="Võitjana ka majanduslikus mõttes väljus võistluselt Vaiko Eplik .", c="võistluselt"),
            assistant_message(a="yes", r="A competition has a time and place."),
    
            user_message(l="Mary ja Frederik sõidavad laulatuselt Amalienborgi lossi .", c="laulatuselt"),
            assistant_message(a="yes", r="A wedding ceremony has a time and place."),
    
            user_message(l="438 Aime Õngo õpetas ateistliku kasvatustöö tegemist keskkooli ajalootundides .", c="ajalootundides"),
            assistant_message(a="yes", r="Classes have a time and usually a place."),
    
            user_message(l="Kaie lubas mind oma proovidesse .", c="proovidesse"),
            assistant_message(a="yes", r="Rehearsals have a time and location."),
    
            user_message(l="Väikelastele mõeldud etenduses tervitavad lapsi erinevatest etendustest pärit nukud.", c="etenduses"),
            assistant_message(a="yes", r="A show or performance has a time and place."),
    
            user_message(l="Nikolajevski muutus töövõimetuks kunagi juhtunud autoavariis .", c="autoavariis"),
            assistant_message(a="yes", r="An event that has a time and place."),

            user_message(l="Samuti pole sabaosas kütusepaake , mis katastroofis suure tõenäosusega süttivad .", c="katastroofis"),
            assistant_message(a="yes", r="An event that will have a time and place."),

            user_message(l="Emana ei lubaks ma oma poega sõtta , ükski ema ei lubaks .", c="sõtta"),
            assistant_message(a="yes", r="An event that will have a time and place."),

            user_message(l="Nii Eesti noormehed kui ka neiud jõudsid EM-i finaalturniirile .", c="finaalturniirile"),
            assistant_message(a="yes", r="An event that has a time and place."),

            user_message(l="Täna sõidavad nad võistluste avamiselt Palermos võistluspaika Cataniasse.", c="avamiselt"),
            assistant_message(a="yes", r="An event that has a time and place."),

            user_message(l="Dokumendi menetlemisel tuli välja palju vigu.", c="menetlemisel"),
            assistant_message(a="yes", r="An event that has a time and inferred place."),

            user_message(l="Eelmisel hooajal pääses Mati esinelikusse.", c="hooajal"),
            assistant_message(a="yes", r="A sports event that has an inferred time and inferred place."),

]

EVENT_FEW_SHOTS_STR = few_shot_dialog_to_text(EVENT_FEW_SHOTS)



TIME_SYSTEM_PROMPT = """
You are a classification assistant.
Your task: Given a list of examples, each with keys "l" (sentence) and "c" (phrase), classify if "c" refers to time in the context of the sentence.
Criteria for time:
- answers question "when?"
- phrase can be replaced by any time indicating word (like today/tomorrow/yesterday) and the sentence will still make sense.
- time (nine o'clock)
- weekday (Monday, Friday)
- months (January, March-April)
- abstract time (in the beginning, in childhood)
- not a situation
- not an event

Analyse the given criteria, analyse the 'few_shots' examples and generalise.
Then process the list called 'batch'.

Output JSON requirements:
- Respond strictly with an array of JSON objects, one object per 'batch' item.
- The JSON array must be in the exact same order as the batch items.
- Response must be without markdown or comments.
- Each output JSON must have:
  "a": "yes" (time) or "no" (not time)
"""

TIME_FEW_SHOTS = [
            user_message(l="Juba Peeter I aegadest on mitmed riigid oma pealinnu kolinud .",c="aegadest"),
            assistant_message(a="yes", r="Since when?"),
    
            user_message(l="Tema sõnul plaanib piigadebänd lõpukontserti aprillikuusse .", c="aprillikuusse"),
            assistant_message(a="yes", r="Month, answers 'when?'."),
    
            user_message(l="Juba lapsepõlves ehitasin endale näiteks baldahhiinvoodi.", c="lapsepõlves"),
            assistant_message(a="yes", r="Answers 'when?'"),
    
            user_message(l="Ta sõi perenaist vaid hädaolukorras , kuna oli ilmselt nädalaid nälginud .", c="hädaolukorras"),
            assistant_message(a="no", r="Situation not time."),
]

TIME_FEW_SHOTS_STR = few_shot_dialog_to_text(TIME_FEW_SHOTS)


