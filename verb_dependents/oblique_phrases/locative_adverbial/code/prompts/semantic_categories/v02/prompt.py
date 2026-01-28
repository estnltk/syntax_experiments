import os 
import sys 

#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../../common_code")))
from common_code.gpt_utils import *


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


FEW_SHOTS_STR = few_shot_dialog_to_text(FEW_SHOTS)


