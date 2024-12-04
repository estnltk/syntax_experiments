# Notebooks

Notebookid, mis loovad järgnevad tabelid:

00 - baastabel analüüsiks: patterns join transaction join transaction_head

	(pat_id, head_id, transaction_id, phrase_nr, verb, deprel, kääne, sõna, koht, elus)

	eraldi "alati" ja "mitte kunagi" isikumäärus verbide jaoks 

01 - obl transaktsioonid, mis on kohakäändes (abl, adit, all, ad, el, ill, in)
	 - distinct sõna count iga verbobl+kääne jaoks 
	 - verbobl koos käände ja distinct sõna count, mis on elus ja koht

02 - obl transaktsioonid
	 - "alati" ja "mitte kunagi" verbidega seotud sõnad
	 - tabelid illustratsioonide jaoks, kus on count sõna koht ja elus jaoks 

03 - obl transaktsioonid grupeeritud sõna lemma alusel ja elus/koht loendus (lemma, lemma_cnt, elus_cnt, koht_cnt)

04 - sõna esinemised mustrites (NB! verb ilma compound)




