## Morfo-süntaksi konfliktid

Siin on toodud hulk süntaksi-morfo konfliktide tabelist leitud konflikte. 

 - *Error rate (transactions)* on antud tüüpi vigade osakaal kõigist antud deprel-i esinemistest transaktsioonide andmebaasis.
 - *Impact (transactions)* on antud tüüpi vigade osakaal kõigist transaktsioonide andmebaasis olevatest tippudest (*transaction head*).
 - *Error rate (syntax-morph conflicts)* on antud tüüpi vigade osakaal kõigist antud deprel-i esinemistest süntaksi-morfoloogia konfliktide tabelis.
 - *Impact (syntax-morph conflicts)* on antud tüüpi vigade osakaal kõigist süntaksi-morfoloogia tabelis olevatest konfliktidest. 
 
Error rate ja impact on skaleeritud 1:100000. 


| description | deprel | case | error rate (transactions) | impact (transactions) | error rate (syntax-morph conflicts) | impact (syntax-morph conflicts)
|---|---|---|---|---|---|---
| kui nsubj ei ole nimetavas/osastavas käändes | nsubj | ^(nom\|part) | 68.2 | 32.03 | 7864.6 | 1471
| kui nsubj:cop ei ole nimetavas/osastavas käändes | nsubj:cop | ^(nom\|part) | 10.89 | 0.01 | 3288.4 | 0.46
| kui obj ei ole nimetavas/omastavas/osastavas käändes| obj | ^(nom\|gen\|part) | 892.95 | 193.47 | 22764.9 | 8884.32
| kui advcl on käändes | advcl | ^0 | 131.72 | 8.69 | 35505.8 | 399.2
| kui advmod on käändes | advmod | ^0 | 4.37 | 0.81 | 181.67 | 37.1
| kui xcomp on käändes | xcomp | ^0 | 120.98 | 10.42 | 34653.25 | 478.3
| kui obl on nimetavas käändes| obl | nom | 137.79 | 42.64 | 12241.96 | 1958.3

NB! xcomp ja advcl UD märgenduse järgi ikkagi võivad olla käändes, samuti esineb UD märgenduses obl nimetavas käändes. Seega ei saa neid siiski käsitleda konkreetsete morfo-süntaksi konfliktidena. Vaja uurida spetsiifilisemalt.