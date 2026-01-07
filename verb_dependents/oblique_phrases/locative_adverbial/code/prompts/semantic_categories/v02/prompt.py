import os 
import sys 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../../common_code")))
from gpt_utils import *


SYSTEM_PROMPT = """
You are a classification assistant.
In this task location refers to "adverbial of place" (Estonian: kohamäärus) or "locative adverb".
Your task: Given a list of examples, each with keys "l" (sentence) and "c" (phrase), classify whether "c" functions as a location in the context of the sentence.
Adverbial of place answers to the question “where” (kus?/kuhu?/kust?) in the context of the sentence.
It is a place or concept where something or someone is located, goes to or comes from.
Criteria:
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

FEW_SHOTS = [
            user_message("Me läksime Pariisi.","Pariisi"),
            assistant_message("yes", "city", "City name, answers question 'where'."),
    
            user_message("Ema on mul olnud alati õmblustöö inimene ja õpetab seda praegu ühes õmbluskoolis teistelegi.", "õmbluskoolis"),
            assistant_message("yes", "location", "Organization's building, answers 'where'."),
    
            user_message("Põhjapoolusele saabus kottide-kompsudega tuhandeid võõrtöölisi.", "Põhjapoolusele"),
            assistant_message("yes", "location", "Answers the question 'to where'."),
    
            user_message("Ta tuli idast kõikide oma raamatutega.", "idast"),
            assistant_message("yes", "direction", "Abstract location, answers 'from where'."),
    
            user_message("Mees istus peale pikka päeva uuesti sadulasse.", "sadulasse"),
            assistant_message("yes", "object", "Man sat on an object and answers 'where'."),

            user_message("Nad sõidavad neljapäeval maale.", "neljapäeval"),
            assistant_message("no", "time", "Answers 'when'."),
    
            user_message("Avo süüdistati selles, et ta varastas magava J.P. põuetaskust raha koos rahakotiga.", "põuetaskust"),
            assistant_message("yes", "object", "Answers 'from where' and is an object."),
    
            user_message("Näiteks korraldas Affleck Lopezile üllatus-sünnipäevapeo restoranis Park.", "restoranis"),
            assistant_message("yes", "location", "Physical location and also organization, answers 'where'."),
    
            user_message("HP700 ei ulatu enam SpeedTouchi Wifi'sse.", "Wifi'sse"),
            assistant_message("yes", "abstract", "Abstract location, answers 'where'"),

            user_message("Minnie käis Barbra teadmata isegi kleidiproovis.", "kleidiproovis"),
            assistant_message("yes", "event", "Event that answers 'where' the person was."),

            user_message("Rüselejal käsisid sussid", "Rüselejal"),
            assistant_message("no", "experiencer", "Rüseleja is the experiencer."),
    
            user_message("Nüüd siis istun sitas.", "sitas"),
            assistant_message("no", "state", "State of being."),    
    
            user_message("Protest on mitmekesine ja teravaimalt avaldub see kirjanduses.", "teravaimalt"),
            assistant_message("no", "other", "Verbial of manner."),    
    
            user_message("Korraldasime seminari TTÜs.", "TTÜs"),
            assistant_message("yes", "location", "TTÜ is an organization but in sentence refers to location and answers 'where'."),
    
            user_message("Väga hästi varjab päikesekiiri näiteks markiis.", "markiis"),
            assistant_message("no", "other", "Nominative case and not location."),
    
            user_message("Ingridi puhul läks hiljem täkkesse just see ütelus.", "täkkesse"),
            assistant_message("no", "other", "Phrasal verb and not location."),
    
            user_message("Mari kuulas kikkis kõrvul.", "kõrvul"),
            assistant_message("no", "manner", "Answers the question 'how'."),
    
            user_message("Maril on kaks last.", "Maril"),
            assistant_message("no", "owner", "Answers the question 'who'."),
    
            user_message("See asi ununes mul täielikult.", "mul"),
            assistant_message("no", "experiencer", "Answers the question 'who'."),
    
            user_message("Luba tal ükskord ometi kõik südamelt ära rääkida.", "tal"),
            assistant_message("no", "experiencer", "Answers the question 'who'."),
    
            user_message("Tüdruku nägu on naerul.", "naerul"),
            assistant_message("no", "state", "Answers the question 'in what state'."),
    
            user_message("Munad on vahul.", "vahul"),
            assistant_message("no", "state", "Answers the question 'in what state'."),
    
            user_message("Mari elab juba kolmandat aastat välismaal.", "välismaal"),
            assistant_message("yes", "location", "Answers the question 'where'."),
    
            user_message("Üliõpilased on loengul.", "loengul"),
            assistant_message("yes", "location", "Answers the question 'where'."),
    
            user_message("Müts on peas.", "peas"),
            assistant_message("yes","location", "Answers the question ‘where’."),
    
            user_message("Jüri on Keskerakonnas.", "Keskerakonnas"),
            assistant_message("yes", "location", "Jüri is located in the organization's structure."),
    
            user_message("Kalle osaleb koalitsioonis.", "koalitsioonis"),
            assistant_message("yes", "location", "Kalle is located in the organization's structure."),
    
            user_message("Tema sünnipäev on märtsis.", "märtsis"),
            assistant_message("no", "time", "Answers question 'when'."),
    
            user_message("Mees on sügavas depressioonis.", "depressioonis"),
            assistant_message("no", "state", "Answers the question 'in what state'."),
    
            user_message("Ta on andekas matemaatikas.", "matemaatikas"),
            assistant_message("no", "construction", "Is purely grammatical."),
    
            user_message("Ma kahtlen teie siiruses.", "siiruses"),
            assistant_message("no", "construction", "Is purely grammatical."),
    
            user_message("Ta mängib orkestris.", "orkestris"),
            assistant_message("yes", "location", "Answers the question 'where'."),
    
            user_message("Rahvamurrus ei leidnud laps ema.", "rahvamurrus"),
            assistant_message("yes", "location", "Answers the question 'where'."),
    
            user_message("Me elame vabaduses, vendluses ja armastuses.", "vabaduses"),
            assistant_message("yes", "location", "Our existence is located in the concept of ‘vabadus’."),
    
            user_message("Sinus on midagi.", "sinus"),
            assistant_message("yes", "location", "Something like a feeling or potential can be located inside of ’sinus’."),
    
            user_message("Maxence märkas ema, hüppas diivanilt püsti ja lülitas televiisori välja, mis äratas emas kohe kahtlusi.", "emas"),
            assistant_message("yes", "location", "kahtlused are located inside of ema. Answers the question ‘where’"),
    
            user_message("Me kasvasime üles botastes.", "botastes"),
            assistant_message("no", "state", "Answers the question 'in what state'."),
    
            user_message("Moos valgus pirukast välja.", "pirukast"),
            assistant_message("yes", "location", "Answers the question 'from where'."),
    
            user_message("Nii voolab riiklikust meditsiinist elujõud muudkui välja .", "meditsiinist"),
            assistant_message("yes", "location", "Conspet, answers the question 'from where'."),
    
            user_message("Uuringu põhjal selgus , et ligi 70 protsenti naistest pöörduks pärast esimese lapse sündi heameelega vanasse töökohta tagasi.", "töökohta"),
            assistant_message("yes", "location", "Answers the question 'to where'."),
    
            user_message("Ema pani Peetrile teki peale.", "Peetrile"),
            assistant_message("yes", "location", "Peeter is not an experiencer in this context, answers the question 'to where'."),
    
            user_message("Toomas Lepp tegutses kaua ETV-s.", "ETV-s"),
            assistant_message("yes", "abstract", "Abstract location, answers 'where'."),
    
            user_message("Ta on lisanud Delfisse mitmeid artikleid.", "Delfisse"),
            assistant_message("yes", "abstract", "Abstract location, answers 'where'."),
    
            user_message("Ta istus hooaja jooksul peatreeneripingile.", "peatreeneripingile"),
            assistant_message("yes", "abstract", "Metaphorical physical movement, answers question 'to where'."),

            user_message("Elu läks rööbastesse tagasi.", "rööbastesse"),
            assistant_message("yes", "abstract", "Metaphorical physical movement, answers question 'to where'."),

            user_message("Organisatsiooni ladvikus on rahu.", "ladvikus"),
            assistant_message("yes", "location", "Peace is a state among the organization's top group, answers question 'where'."),

            user_message("Elus tuleb ikka takistusi ette.", "Elus"),
            assistant_message("yes", "location", "Life refers to abstract location, answers question 'where'."),

            user_message("Sakslastele valgus peale rünnakute laviin.", "Sakslastele"),
            assistant_message("yes", "location", "Germans are not experiences but abstract location of attacks, answers question 'onto where'."),

            user_message("Eile külastas pottseppa tema vana sõber.", "pottseppa"),
            assistant_message("no", "experiencer", "Answers 'who' was visited."),
             
            user_message("Ema sõidutab mind trenni.", "trenni"),
            assistant_message("yes", "location", "Answers the question 'where'."),
             
            user_message("Selles valguses paistavad asjad hullemad.", "valguses"),
            assistant_message("yes", "abstract", "Light becomes conceptual place, answers the question 'where'."),
             
            user_message("Ta viskas asjad kotti.", "kotti"),
            assistant_message("yes", "location", "Answers the question 'where'."),
             
            user_message("Mind saadeti uksest välja.", "uksest"),
            assistant_message("yes", "object", "Answers the question 'through where'."),
             
            user_message("Kurbus ei mahu näkku ära.", "näkku"),
            assistant_message("yes", "abstract", "Answers the question 'where'."),
             
            # kui lisada see, siis mudel arvab et "liblikas maandub emale" ei ole asukoht enam
            #user_message("Kui võtaks kellegi neist endaga kaasa?", "neist"),
            #assistant_message("no", "other", "Source set, not a spatial frame."),  
    
]


FEW_SHOTS_STR = messages_2_str(FEW_SHOTS)


