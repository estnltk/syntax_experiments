# v12
Kollokatsiooniandmete salvestamisel tabelisse jäeti välja kollokatsioonid, milles:

* verb oli umbisikuline (<code>feats</code> sisaldas parameetrit <code>imps</code>);
* verbi aeg polnud ükski järgnevatest: <code>past</code>, <code>impf</code>, <code>pres</code> (<code>feats</code> ei sisaldanud parameetreid <code>past</code> ega <code>impf</code> ega  <code>pres</code>).

### Tabelid

### TABEL1 
**verb\_compound\_obl**

Paksu kirjaga on märgitud väljad, mis moodustavad unikaalse indeksi.

| väli | tüüp  |  kirjeldus | näide | märkus |
| --- | --- | --- | --- | --- |
| id | int | kollokatsiooni<br/>unikaalne ID| *56* | |
| **verb** | text | tegusõna lemma | *kirjutama* | |
| **verb_compound** | text | määrsõna(de) lemma(d) | *alla,kokku* | mitme määrsõna korral on lemmade eraldajaks koma ja lemmad on alfabeetilises järjestuses |
| **obl_root** | text| täiendi juure lemma nn "puhastatud kuju"| *kurjajuur* | |
| **obl\_root\_compound** | text| täiendi juure lemma liitsõnamärkidega*| *kurja_juur* | |
| **obl_case** | text | täiendi juure kääne | *ad* | vt [Käänded](#käänded) |
| **obl_k** | text | täiendi juurele alluv kaassõna lemma  | *peale* | tipp, mille <code>deprel=case</code> ja <code>pos=K</code>,<br/>mitme määrsõna korral on lemmade eraldajaks koma, lemmad on alfabeetilises järjestuses |
| **ner_loc** | text | täiendi fraasi asetus NER 'LOC' spani suhtes  | *intersects* | vt [OBL asetus](#obl_asetus) |
| **ner_per** | text | --\|\|-- 'PER' spani suhtes | *match* | vt [OBL asetus](#obl_asetus) |
| **ner_org** | text | --\|\|-- 'ORG' spani suhtes | *contains* | vt [OBL asetus](#obl_asetus) |
| **timex** | text |  --\|\|-- TIMEX spani suhtes | *-* | vt [OBL asetus](#obl_asetus)|
| count | int | kollokatsiooni esinemiste arv üle korpuse | *56* |  | 
| phrase_type | text | täiendi fraasi tüüp | *null* |   täitmata |

### TABEL2 

**verb\_compound\_obl\_examples**


| väli | tüüp  |  kirjeldus |	näide | märkus |
| --- | --- | --- | --- | --- |
| **row_id** | int | rea id tabelis TABEL1| | |
| **sentence_id** | int | kollektsiooni id postgres andmebaasis | | |
| **root_id** | int | OBL fraasi juur (sõna nr) | | |
| count | int | mitu korda näide esines |  | täitsa võimalik, et selle välja väärtus on antud versiooni tabelis alati 1 |




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


