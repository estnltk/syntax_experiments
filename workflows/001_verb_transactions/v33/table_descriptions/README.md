
## transactions andmebaasi tabelid

### TABEL1 transaction_head

| väli | tüüp  |  kirjeldus | näide | märkus |
| --- | --- | --- | --- | --- |
| id | int | rea <br/>unikaalne ID| *56* | |
| sentence_id | int | lause id andmebaasis| | |
| loc | int | verbi asukoht lauses | | |
| verb | text |verbi lemma | *olema*| |
| verb_compound | text | verbi afiksaaladverbid| alla,peale| eraldajaks koma |
| form | text | verb sellises vormis, nagu see lauses esines| *oli* | |
| deprel | text | verbi deprel | | |
| feats | text | verbi morf kategooriad alfabeetilises järjekorras | aux,ps3||
| phrase | text | puhastatud fraas (ainult need alluvad, mis on transactiosn tabelisse salvestatud) | ||



### TABEL2 transaction

| väli | tüüp  |  kirjeldus | näide | märkus |
| --- | --- | --- | --- | --- |
| id | int | rea <br/>unikaalne ID| *56* | |
| head_id | int| rea transaction_head.id  | | |
| loc | int | sõna asukoht lauses | | |
| loc_rel | int | sõna asukoht verbi suhtes  | | |
| deprel | text | sõna deprel | | |
| form | text | sõna vorm  | | |
| lemma |  text | sõna lemma | | |
| pos | text | sõna sõnaliik | | |
| feats | text|  sõna morf kategooriad alfabeetilises järjekorras |  add,sg| |
| parent_loc | int | vanema tipu loc, juhul kui tegemist on <code>obl</obl> alluvaga  case|  2| |

