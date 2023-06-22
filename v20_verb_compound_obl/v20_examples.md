|   tulp   | tüüp |   kirjeldus    |      kommentaar      |
|------|---|-------------------------|--------------|
| verb          | text | tegusõna lemma       |             |
| verb_compound | text | määrsõna(de) lemma(d)     | mitme määrsõna korral on lemmade eraldajaks koma ja lemmad on alfabeetilises järjestuses |
| obl_case      | text | täiendi juure kääne                                   |
| total         | int | esinemiste arv (verb+verb\_compound+obl_case)      |
| obl_lemma	    | text | täiendi juure lemma | |
| row_ids       | text | ridade id-d  verb\_compound\_obl tabelist     | eraldajaks koma      |
| random_example | int | juhuslik id row_ids väljalt        | |
| sentence_id   | int | lause/collection id postgres andmebaasis ||
| root_id	      | int | täiendi juure word id      |           |
| verb_id       | int | tegusõna word id       |     |
| 	compound_ids | text | määrsõna(de) word id-d  | eraldajaks koma  |
| 	obl_ids      | text | täiendi liikmete word id-d   | eraldajaks koma |
| 	verb_span	   | json | tegusõna span | |
| obl_span	     | json | täiendi juure span | |
| sentence	     | text| lause text |  | 
| compound_spans	 | json | määrsõna(de) spanid | |
| oblp_spans    | json | obl fraasi spanid | | 
