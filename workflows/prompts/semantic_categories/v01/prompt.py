import os 
import sys 

from common_code.gpt_utils import *


LOC_SYSTEM_PROMPT = """
You are a classification assistant.
In this task location refers to "adverbial of place" (Estonian: kohamäärus) or "locative adverb".
Your task: Given a list of examples, each with keys "l" (sentence) and "c" (phrase), classify whether "c" functions as a location in the context of the sentence.
Adverbial of place answers to the question “where” (kus?/kuhu?/kust?) in the context of the sentence.
Criteria:
- It is a place or concept where something or someone is located, goes to or comes from.
- concrete place (bank, table, Berlin)
- abstract (literature, soul, TV channels, government, top of a group, history, thought, domain)
- inanimate (journal, chair, wifi, bag, medal, toy, food, computer, wire, body parts)
- alive (mother, Peter, dog, doctor, teacher)
- event (dress rehearsal, camp, class, situation, meeting)
- state or condition conceptualized as space (life, trouble, consciousness, attitude)
- Locations ARE NOT phrases that show time, state of being, owner, experiencer, instrument, manner OR are purely grammatical constructions. 
- If the phrase can answer the question when, in what state, who, with what or how, then it is not a location.
Analyse the given criteria of location, analyse the 'few_shots' examples and generalise.
Then process the list called 'batch'.
Output JSON requirements:
- Respond strictly with an array of JSON objects, one object per 'batch' item.
- The JSON array must be in the exact same order as the batch items.
- Response must be without markdown or comments.
- Each output JSON must have:
  "a": "yes" (location) or "no" (not location)
"""


LOC_SYSTEM_PROMPT2 = """
You are a classification assistant.
In this task location refers to "adverbial of place" (Estonian: kohamäärus) or "locative adverb".
Your task: Given a list of examples, each with keys "l" (sentence) and "c" (phrase), classify whether "c" functions as a location in the context of the sentence.
Adverbial of place answers to the question “where” (kus?/kuhu?/kust?) in the context of the sentence.
It is a place or concept where something or someone is located, goes to or comes from.
Criteria:
- Phrase is NOT a location if it answers questions when, in what state, who, with what or how.
- Phrase is a location if it answers questions where, from where, to where.
Examples of locations:
- concrete place (bank, table, Berlin)
- abstract (literature, soul, TV channels, government, top of a group, history, thought, domain)
- inanimate (journal, chair, wifi, bag, medal, toy, food, computer, wire, body parts)
- alive if the person/entity is source or destination location (to mother, onto Peter, on top of dog, doctor, out of teacher)
Analyse the given criteria and examples of location, analyse the 'few_shots' examples and generalise.
Then process the list called 'batch'.
Output JSON requirements:
- Respond strictly with an array of JSON objects, one object per 'batch' item.
- The JSON array must be in the exact same order as the batch items.
- Response must be without markdown or comments.
- Each output JSON must have:
  "a": "yes" (location) or "no" (not location)
"""

LOC_FEW_SHOTS = [
            user_message(l="Me läksime Pariisi.",c="Pariisi"),
            assistant_message(a="yes", s="city", r="City name, answers question 'where'."),
    
            user_message(l="Ema on mul olnud alati õmblustöö inimene ja õpetab seda praegu ühes õmbluskoolis teistelegi.", c="õmbluskoolis"),
            assistant_message(a="yes", s="location", r="Organization's building, answers 'where'."),
    
            user_message(l="Põhjapoolusele saabus kottide-kompsudega tuhandeid võõrtöölisi.", c="Põhjapoolusele"),
            assistant_message(a="yes", s="location", r="Answers the question 'to where'."),
    
            user_message(l="Ta tuli idast kõikide oma raamatutega.", c="idast"),
            assistant_message(a="yes", s="direction", r="Abstract location, answers 'from where'."),
    
            user_message(l="Mees istus peale pikka päeva uuesti sadulasse.",c= "sadulasse"),
            assistant_message(a="yes", s="object", r="Man sat on an object and answers 'where'."),

            user_message(l="Nad sõidavad neljapäeval maale.", c="neljapäeval"),
            assistant_message(a="no", s="time", r="Answers 'when'."),
    
            user_message(l="Avo süüdistati selles, et ta varastas magava J.P. põuetaskust raha koos rahakotiga.", c="põuetaskust"),
            assistant_message(a="yes", s="object", r="Answers 'from where' and is an object."),
    
            user_message(l="Näiteks korraldas Affleck Lopezile üllatus-sünnipäevapeo restoranis Park.", c="restoranis"),
            assistant_message(a="yes", s="location", r="Physical location and also organization, answers 'where'."),
    
            user_message(l="HP700 ei ulatu enam SpeedTouchi Wifi'sse.", c="Wifi'sse"),
            assistant_message(a="yes", s="abstract", r="Abstract location, answers 'where'"),

            user_message(l="Minnie käis Barbra teadmata isegi kleidiproovis.", c="kleidiproovis"),
            assistant_message(a="yes", s="event", r="Event that answers 'where' the person was."),

            user_message(l="Rüselejal käsisid sussid", c="Rüselejal"),
            assistant_message(a="no", s="experiencer", r="Rüseleja is the experiencer."),
    
            user_message(l="Nüüd siis istun sitas.", c="sitas"),
            assistant_message(a="no", s="state", r="State of being."),    
    
            user_message(l="Protest on mitmekesine ja teravaimalt avaldub see kirjanduses.", c="teravaimalt"),
            assistant_message(a="no", s="other", r="Verbial of manner."),    
    
            user_message(l="Korraldasime seminari TTÜs.", c="TTÜs"),
            assistant_message(a="yes", s="location", r="TTÜ is an organization but in sentence refers to location and answers 'where'."),
    
            user_message(l="Väga hästi varjab päikesekiiri näiteks markiis.", c="markiis"),
            assistant_message(a="no", s="other", r="Nominative case and not location."),
    
            user_message(l="Ingridi puhul läks hiljem täkkesse just see ütelus.", c="täkkesse"),
            assistant_message(a="no", s="other", r="Phrasal verb and not location."),
    
            user_message(l="Mari kuulas kikkis kõrvul.", c="kõrvul"),
            assistant_message(a="no", s="manner", r="Answers the question 'how'."),
    
            user_message(l="Maril on kaks last.", c="Maril"),
            assistant_message(a="no", s="owner", r="Answers the question 'who'."),
    
            user_message(l="See asi ununes mul täielikult.", c="mul"),
            assistant_message(a="no", s="experiencer", r="Answers the question 'who'."),
    
            user_message(l="Luba tal ükskord ometi kõik südamelt ära rääkida.", c="tal"),
            assistant_message(a="no", s="experiencer", r="Answers the question 'who'."),
    
            user_message(l="Tüdruku nägu on naerul.", c="naerul"),
            assistant_message(a="no", s="state", r="Answers the question 'in what state'."),
    
            user_message(l="Munad on vahul.", c="vahul"),
            assistant_message(a="no", s="state", r="Answers the question 'in what state'."),
    
            user_message(l="Mari elab juba kolmandat aastat välismaal.", c="välismaal"),
            assistant_message(a="yes", s="location", r="Answers the question 'where'."),
    
            user_message(l="Üliõpilased on loengul.", c="loengul"),
            assistant_message(a="yes", s="location", r="Answers the question 'where'."),
    
            user_message(l="Müts on peas.", c="peas"),
            assistant_message(a="yes",s="location", r="Answers the question ‘where’."),
    
            user_message(l="Jüri on Keskerakonnas.", c="Keskerakonnas"),
            assistant_message(a="yes", s="location", r="Jüri is located in the organization's structure."),
    
            user_message(l="Kalle osaleb koalitsioonis.", c="koalitsioonis"),
            assistant_message(a="yes", s="location", r="Kalle is located in the organization's structure."),
    
            user_message(l="Tema sünnipäev on märtsis.", c="märtsis"),
            assistant_message(a="no", s="time", r="Answers question 'when'."),
    
            user_message(l="Mees on sügavas depressioonis.", c="depressioonis"),
            assistant_message(a="no", s="state", r="Answers the question 'in what state'."),
    
            user_message(l="Ta on andekas matemaatikas.", c="matemaatikas"),
            assistant_message(a="no", s="construction", r="Is purely grammatical."),
    
            user_message(l="Ma kahtlen teie siiruses.", c="siiruses"),
            assistant_message(a="no", s="construction", r="Is purely grammatical."),
    
            user_message(l="Ta mängib orkestris.", c="orkestris"),
            assistant_message(a="yes", s="location", r="Answers the question 'where'."),
    
            user_message(l="Rahvamurrus ei leidnud laps ema.", c="rahvamurrus"),
            assistant_message(a="yes", s="location", r="Answers the question 'where'."),
    
            user_message(l="Me elame vabaduses, vendluses ja armastuses.", c="vabaduses"),
            assistant_message(a="yes", s="location", r="Our existence is located in the concept of ‘vabadus’."),
    
            user_message(l="Sinus on midagi.", c="sinus"),
            assistant_message(a="yes", s="location", r="Something like a feeling or potential can be located inside of ’sinus’."),
    
            user_message(l="Maxence märkas ema, hüppas diivanilt püsti ja lülitas televiisori välja, mis äratas emas kohe kahtlusi.", c="emas"),
            assistant_message(a="yes", s="location", r="kahtlused are located inside of ema. Answers the question ‘where’"),
    
            user_message(l="Me kasvasime üles botastes.", c="botastes"),
            assistant_message(a="no", s="state", r="Answers the question 'in what state'."),
    
            user_message(l="Moos valgus pirukast välja.", c="pirukast"),
            assistant_message(a="yes", s="location", r="Answers the question 'from where'."),
    
            user_message(l="Nii voolab riiklikust meditsiinist elujõud muudkui välja .", c="meditsiinist"),
            assistant_message(a="yes", s="location", r="Conspet, answers the question 'from where'."),
    
            user_message(l="Uuringu põhjal selgus , et ligi 70 protsenti naistest pöörduks pärast esimese lapse sündi heameelega vanasse töökohta tagasi.", c="töökohta"),
            assistant_message(a="yes", s="location", r="Answers the question 'to where'."),
    
            user_message(l="Ema pani Peetrile teki peale.", c="Peetrile"),
            assistant_message(a="yes", s="location", r="Peeter is not an experiencer in this context, answers the question 'to where'."),
    
            user_message(l="Toomas Lepp tegutses kaua ETV-s.", c="ETV-s"),
            assistant_message(a="yes", s="abstract", r="Abstract location, answers 'where'."),
    
            user_message(l="Ta on lisanud Delfisse mitmeid artikleid.", c="Delfisse"),
            assistant_message(a="yes", s="abstract", r="Abstract location, answers 'where'."),
    
            user_message(l="Ta istus hooaja jooksul peatreeneripingile.", c="peatreeneripingile"),
            assistant_message(a="yes", s="abstract", r="Metaphorical physical movement, answers question 'to where'."),

            user_message(l="Elu läks rööbastesse tagasi.", c="rööbastesse"),
            assistant_message(a="yes", s="abstract", r="Metaphorical physical movement, answers question 'to where'."),

            user_message(l="Organisatsiooni ladvikus on rahu.", c="ladvikus"),
            assistant_message(a="yes", s="location", r="Peace is a state among the organization's top group, answers question 'where'."),

            user_message(l="Elus tuleb ikka takistusi ette.", c="Elus"),
            assistant_message(a="yes", s="location", r="Life refers to abstract location, answers question 'where'."),

            user_message(l="Sakslastele valgus peale rünnakute laviin.", c="Sakslastele"),
            assistant_message(a="yes", s="location", r="Germans are not experiences but abstract location of attacks, answers question 'onto where'."),

            user_message(l="Eile külastas pottseppa tema vana sõber.", c="pottseppa"),
            assistant_message(a="no", s="experiencer", r="Answers 'who' was visited."),
             
            user_message(l="Ema sõidutab mind trenni.", c="trenni"),
            assistant_message(a="yes", s="location", r="Answers the question 'where'."),
             
            user_message(l="Selles valguses paistavad asjad hullemad.", c="valguses"),
            assistant_message(a="yes", s="abstract", r="Light becomes conceptual place, answers the question 'where'."),
             
            user_message(l="Ta viskas asjad kotti.", c="kotti"),
            assistant_message(a="yes", s="location", r="Answers the question 'where'."),
             
            user_message(l="Mind saadeti uksest välja.", c="uksest"),
            assistant_message(a="yes", s="object", r="Answers the question 'through where'."),
             
            user_message(l="Kurbus ei mahu näkku ära.", c="näkku"),
            assistant_message(a="yes", s="abstract", r="Answers the question 'where'."),
             
            # kui lisada see, siis mudel arvab et "liblikas maandub emale" ei ole asukoht enam
            #user_message("Kui võtaks kellegi neist endaga kaasa?", "neist"),
            #assistant_message("no", "other", "Source set, not a spatial frame."),  
    
]


LOC_FEW_SHOTS_STR = few_shot_dialog_to_text(LOC_FEW_SHOTS)



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



STATE_SYSTEM_PROMPT = """
You are a classification assistant.
Your task: Given a list of examples, each with keys "l" (sentence) and "c" (phrase), classify if "c" refers to a state of being in the context of the sentence.
Ask internally: In the context of this sentence, does the phrase denote a state of being (Estonian: seisund või seisundimäärus), meaning it describes a condition, status, or ongoing state (like physical condition, psychological condition, marital status, social status, financial situation, weather conditions etc) rather than an action or event?
Criteria for state:
- condition of being
- status of being
- ongoing state
- Is NOT an action (toimetamine, toetamine, rahastamine, etc) .
- Is NOT a time phrase (minevik, periood, etc)

Analyse the given criteria, analyse the 'few_shots' examples and generalise. Ignore capitalization. Do not assume — context determines meaning.
Then process the list called 'batch'.

Output JSON requirements:
- Respond strictly with an array of JSON objects, one object per 'batch' item.
- The JSON array must be in the exact same order as the batch items.
- Response must be without markdown or comments.
- Each output JSON must have:
  "a": "yes" (state of being) or "no" (not a state of being)
"""

STATE_FEW_SHOTS = [

            user_message(l="Tüdruku nägu on naerul.", c="naerul"),
            assistant_message(a="yes", s="state", r="Answers the question 'in what state'."),
    
            user_message(l="Munad on vahul.", c="vahul"),
            assistant_message(a="yes", s="state", r="Answers the question 'in what state'."),
    
            user_message(l="Mees on sügavas depressioonis.", c="depressioonis"),
            assistant_message(a="yes", s="state", r="Answers the question 'in what state'."),

            user_message(l="Me kasvasime üles botastes.", c="botastes"),
            assistant_message(a="yes", s="state", r="Answers the question 'in what state'."),
    
            user_message(l="Nüüd siis istun sitas.", c="sitas"),
            assistant_message(a="yes", s="state", r="State of being."),  
    
            user_message(l="Nad olid 10 aastat abielus.", c="abielus"),
            assistant_message(a="yes", s="state", r="Status."), 
    
            user_message(l="Raske on sellises olukorras närvipingest üle saada.", c="närvipingest"),
            assistant_message(a="yes", s="state", r="State of being, condition."),
    
            user_message(l="Soojatundest unistab talvel igaüks.", c="Soojatundest"),
            assistant_message(a="yes", s="state", r="State of being, condition."),
    
            user_message(l="Ma käin ülikoolis loengus.", c="ülikoolis"),
            assistant_message(a="no", r="Physical location."),

            user_message(l="Nõukogu on siiamaani lähtunud investeeringute toetamisel ühest põhimõttest.", c="toetamisel"),
            assistant_message(a="no", r="An action that the organization takes."),

            user_message(l="Noored käisid Suusaliidu kulul puhkusel.", c="kulul"),
            assistant_message(a="no", r="Describes how the vacation was funded, not the state of the vacation or its participants."),

            user_message(l="Kooli hinnangul on asi halb.", c="hinnangul"),
            assistant_message(a="no", r="Opinion, not a state."),

            user_message(l="ÜRO ettepanekul viidi sisse muudatud.", c="ettepanekul"),
            assistant_message(a="no", r="Action or reason, not a state"),
]

STATE_FEW_SHOTS_STR = few_shot_dialog_to_text(STATE_FEW_SHOTS)





ORG_SYSTEM_PROMPT = """
You are a classification assistant.
Your task: Given a list of examples, each with keys "l" (sentence) and "c" (phrase), classify if "c" refers to an organization in the context of the sentence.
Ask internally: In the context of this sentence, does the phrase denote an institution acting or capable of acting, rather than merely a place?
Criteria for organization:
- An entity that can function as a collective decision-maker or actor.
- Consists of people in a structured system
- Can act, decide, fund, regulate, employ, announce, or govern
- Exists beyond just a physical building, location, venue or general environment
- Is NOT an action (toimetamine, toetamine, rahastamine, etc) .

Analyse the given criteria, analyse the 'few_shots' examples and generalise. Ignore capitalization. Do not assume that every school, hospital, bank, or university is automatically an organization — context determines meaning.
Then process the list called 'batch'.

Output JSON requirements:
- Respond strictly with an array of JSON objects, one object per 'batch' item.
- The JSON array must be in the exact same order as the batch items.
- Response must be without markdown or comments.
- Each output JSON must have:
  "a": "yes" (organization) or "no" (not organization)
"""

ORG_FEW_SHOTS = [
            user_message(l="Riik andis ülikoolile raha .",c="ülikoolile"),
            assistant_message(a="yes", r="Organization received money."),
    
            user_message(l="Ma käin ülikoolis loengus.", c="ülikoolis"),
            assistant_message(a="no", r="Physical location."),
    
            user_message(l="Ministeeriumis otsustati seadust muuta.", c="Ministeeriumis"),
            assistant_message(a="yes", r="Organization making changes."),
    
            user_message(l="Ta ootas haiglas arsti.", c="haiglas"),
            assistant_message(a="no", r="Physical location"),

            user_message(l="Nõukogu on siiamaani lähtunud investeeringute toetamisel ühest põhimõttest.", c="toetamisel"),
            assistant_message(a="no", r="An action that the organization takes."),

            user_message(l="Noored käisid Suusaliidu kulul puhkusel.", c="kulul"),
            assistant_message(a="no", r="Organization funds the vacation but the phrase is not and organization."),

            user_message(l="Kooli hinnangul on asi halb.", c="hinnangul"),
            assistant_message(a="no", r="Opinion and not an organization."),

            user_message(l="ÜRO ettepanekul viidi sisse muudatud.", c="ettepanekul"),
            assistant_message(a="no", r="Action and not an organization."),

            user_message(l="Meie kooli nõukogu otsusel loodi uusi töökohti.", c="otsusel"),
            assistant_message(a="no", r="Action and not an organization."),

]

ORG_FEW_SHOTS_STR = few_shot_dialog_to_text(ORG_FEW_SHOTS)



