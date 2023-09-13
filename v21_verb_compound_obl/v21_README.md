# v21
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
| count | int | kollokatsiooni esinemiste arv üle korpuse | *56* |  | 

### TABEL2 

**verb\_compound\_obl\_examples**


| väli | tüüp  |  kirjeldus |	näide | märkus |
| --- | --- | --- | --- | --- |
| **row_id** | int | rea id tabelis TABEL1| | |
| **sentence_id** | int | kollektsiooni id postgres andmebaasis | | |
| **root_id** | int | OBL fraasi juur (sõna nr) | | |
| verb_id | int | verbi id (sõna nr) | | |
| compound_ids | text | määrsõna(de) id(-d) (sõna nr) | | |
| obl_ids | text | täiendi fraasi kõik liikmed | | |
| obl_count | int | lauses esinevate osalausete arv<br>1 -> lihtlause | | |

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


