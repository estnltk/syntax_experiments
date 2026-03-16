## Morfo-süntaksi konfliktid

Siin on toodud hulk süntaksi-morfo konfliktide tabelist leitud konflikte. *Error rate* on antud tüüpi vigade osakaal kõigist antud deprel-i esinemistest transaktsioonide andmebaasis. *Impact* on antud tüüpi vigade osakaal kõigist transaktsioonide andmebaasis olevatest tippudest (*transaction head*). Mõlemad arvud on skaleeritud 1:100000. 

| description | deprel | case | error rate | impact
|---|---|---|---|---
| kui nsubj ei ole nimetavas/osastavas käändes | nsubj | ^(nom\|part) | 68.2 | 32.03
| kui nsubj:cop ei ole nimetavas/osastavas käändes | nsubj:cop | ^(nom\|part) | 10.89 | 0.01
| kui obj ei ole nimetavas/omastavas/osastavas käändes| obj | ^(nom\|gen\|part) | 892.95 | 193.47
| kui advcl on käändes | advcl | ^0 | 131.72 | 8.69
| kui advmod on käändes | advmod | ^0 | 4.37 | 0.81
| kui xcomp on käändes | xcomp | ^0 | 120.98 | 10.42
| kui obl on nimetavas käändes| obl | nom | 137.79 | 42.64