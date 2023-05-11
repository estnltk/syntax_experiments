

# v10
Kollokatsiooniandmete salvestamisel tabelisse jäeti välja kollokatsioonid, milles:

* verb oli umbisikuline (<code>feats</code> sisaldas paramteetrit <code>imps</code>);
* verbi aeg polnud ükski järgnevatest: <code>past</code>, <code>impf</code>, <code>pres</code> (<code>feats</code> ei sisaldanud parameetreid <code>past</code> ega <code>impf</code> ega  <code>pres</code>).

### Tabelid
**verb\_compound\_obl\_koondkorpus\_sentences**

| väli | tüüp  |  kirjeldus | näide | märkus |
| --- | --- | --- | --- | --- |
| **id** | int | kollokatsiooni<br/>unikaalne ID| *56* | |
| **verb** | text | tegusõna lemma | *kirjutama* | |
| **verb_compound** | text | määrsõna(de) lemma(d) | *alla,kokku* | mitme määrsõna korral on lemmade eraldajaks koma ja lemmad on alfabeetilises järjestuses |
| **obl_root** | text| täiendi juure lemma| *reede* | |
| **obl_case** | text | täiendi juure kääne | *ad* | vt [Käänded](#käänded) |
| **ner_loc** | text | täiendi fraasi asetus NER 'LOC' spani suhtes  | *intersects* | vt [OBL asetus](#obl_asetus) |
| **ner_per** | text | --\|\|-- 'PER' spani suhtes | *match* | vt [OBL asetus](#obl_asetus) |
| **ner_org** | text | --\|\|-- 'ORG' spani suhtes | *contains* | vt [OBL asetus](#obl_asetus) |
| **timex** | text |  --\|\|-- TIMEX spani suhtes | *-* | vt [OBL asetus](#obl_asetus)|
| **count** | int | kollokatsiooni esinemiste arv üle korpuse | *56* |  | 
| **phrase_type** | text | täiendi fraasi tüüp | *null* |   täitmata |

**verb\_compound\_obl\_koondkorpus\_sentences\_examples**

| väli | tüüp  |  kirjeldus |	näide | märkus |
| --- | --- | --- | --- | --- |
| colId	| int	| *56* |kollokatsiooni id tabelist **verb\_compound\_obl\_koondkorpus\_sentences**|
| examples | text	| 123,678,334| komadega eraldatud kollektsioonide ID-d, kus vastav kollokatsioon esines |


### OBL asetus
| väärtus | kirjeldus  |  
| --- | --- |
| **-** |           OBL ei ole kautud ühegi spaniga|
| **match** |      OBL span langeb kokku NER/TIMEX spaniga|
| **contains** |    OBL spani sees on NER/TIMEX span|
| **inside** |        OBL span on  NER/TIMEX spani sees|
| **intersects** |  OBL span lõikub NER/TIMEX spaniga|



### Käänded
| kääne|  nimetus| 
| --- | --- |
| nom |  nimetav | 
| gen | omastav | 
| part | osastav | 
| adit | lühike sisseütlev | 
| ill | sisseütlev | 
| in |  seesütlev | 
| el |  seestütlev | 
| all |  alaleütlev |
| ad |  alalütlev | 
| abl |  alaltütlev | 
| tr | saav | 
| term |  rajav | 
| es |  olev | 
| abes |  ilma | 
| kom | kaasa | 
| \<käändumatu\> | täiendil puudus kääne | 


