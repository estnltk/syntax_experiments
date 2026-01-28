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



ABSTRACT_SYSTEM_PROMPT = """
You are a classification assistant.
Your task: Given a list of examples, each with keys "l" (sentence) and "c" (phrase), classify if "c" refers to an abstract place in the context of the sentence.
Criteria for abstract place (internal reasoning):
1. An abstract location adverbial answers “Where?” in a non-physical domain (text, mind, system, theory) and cannot be rephrased as time, manner, cause, or condition.
2. Does it answer “Where?” If yes -> is abstract location.
3. Does it place the event/state somewhere, even metaphorically? If yes -> is abstract location.
4. Could this “where” exist without physical space? Yes -> abstract location; No -> concrete location.
5. Can the phrase can be replaced with "somewhere" ("kuskil") and the sentence will still make sense? If yes -> is abstract location
6. Replaceable by time words? -> Not abstract location
7. Means condition (if X)? -> Not abstract location
8. Describes how something happens? -> Not abstract location

Analyse all criteria, analyse the 'few_shots' examples and generalise.
Then process the list called 'batch' based on the criteria.

Output JSON requirements:
- Respond strictly with an array of JSON objects, one object per 'batch' item.
- The JSON array must be in the exact same order as the batch items.
- Response must be without markdown or comments.
- Each output JSON must have:
  "a": "yes" (abstract location) or "no" (not abstract location)
"""

ABSTRACT_FEW_SHOTS = [
            user_message(l="Toomas Lepp tegutses kaua ETV-s.", c="ETV-s"),
            assistant_message(a="yes", s="abstract", r="Abstract location, answers 'where'."),
    
            user_message(l="HP700 ei ulatu enam SpeedTouchi Wifi'sse.", c="Wifi'sse"),
            assistant_message(a="yes", r="Abstract location, answers 'where'"),
    
            user_message(l="Sel aastal on suhtumine linnaeluprobleemidesse heas mõttes muutuma hakanud .", c="linnaeluprobleemidesse"),
            assistant_message(a="yes", r="Abstract location, answers 'where'"),
    
            user_message(l="Ta on lisanud Delfisse mitmeid artikleid.", c="Delfisse"),
            assistant_message(a="yes", r="Abstract location, answers 'where'."),
    
            user_message(l="Ta istus hooaja jooksul peatreeneripingile.", c="peatreeneripingile"),
            assistant_message(a="yes", r="Metaphorical physical movement, answers question 'to where'."),
    
            user_message(l="Elu läks rööbastesse tagasi.", c="rööbastesse"),
            assistant_message(a="yes", r="Metaphorical physical movement, answers question 'to where'."),
    
            user_message(l="Elus tuleb ikka takistusi ette.", c="Elus"),
            assistant_message(a="yes", r="Life refers to abstract location, answers question 'where'."),
    
            user_message(l="Elukorralduses tuleb teha muudatusi.", c="Elukorralduses"),
            assistant_message(a="yes", r="Life refers to abstract location, answers question 'where'."),
    
            user_message(l="Selles valguses paistavad asjad hullemad.", c="valguses"),
            assistant_message(a="yes", r="Light becomes conceptual place, answers the question 'where'."),
    
            user_message(l="Ta tuli idast kõikide oma raamatutega.", c="idast"),
            assistant_message(a="yes", r="Abstract location, answers 'from where'."),
    
            user_message(l="Nüüd siis istun sitas.", c="sitas"),
            assistant_message(a="no",r="State of being."), 
    
            user_message(l="Ingridi puhul läks hiljem täkkesse just see ütelus.", c="täkkesse"),
            assistant_message(a="no", r="Phrasal verb and not location."),
    
            user_message(l="Mari kuulas kikkis kõrvul.", c="kõrvul"),
            assistant_message(a="no", r="Answers the question 'how'."),
            
            user_message(l="Munad on vahul.", c="vahul"),
            assistant_message(a="no", r="Answers the question 'in what state'."),
            
            user_message(l="Tema sünnipäev on märtsis.", c="märtsis"),
            assistant_message(a="no", r="Answers question 'when'."),
    
            user_message(l="Mees on sügavas depressioonis.", c="depressioonis"),
            assistant_message(a="no", r="Answers the question 'in what state'."),
    
            user_message(l="Ta on andekas matemaatikas.", c="matemaatikas"),
            assistant_message(a="no", r="Is purely grammatical."),
            
    
]

ABSTRACT_FEW_SHOTS_STR = few_shot_dialog_to_text(ABSTRACT_FEW_SHOTS)



TIME_SYSTEM_PROMPT = """
You are a classification assistant.
Your task: Given a list of examples, each with keys "l" (sentence) and "c" (phrase), classify if "c" refers to time in the context of the sentence.
Criteria for time:
- answers question "when?"
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


