### Casepairs research documentation



Our goal is to find a way to automatically annotate semantic/adverbial types onto obliques in spatial cases (additive, illative, allative, inessive, adessive, elative, ablative) in Estonian. For that purpose we look at pairs of obliques that have the same head verb with different combinations of morphological cases. We do this to find whether these pairing form coherent patterns of semantic/adverbial types or tagging errors and research what additional conditions are needed for them to form (ie verb type, case order, argumentativeness etc). Doing that allows us to filter out errors and semantic anomalies from verb-case patterns (ie - a verb + oblique in illative case is a location 90% of the time, so under what conditions do the other 10% of patterns form so that we could filter them out). 



#### Casepairs.xslx column name and value explanations



**case\_pair** - combination of spatial cases that a verb's two direct dependents have in the same sentence. Cases are presented in the order they appear in in the sentence (so inessive+elative does not equal elative+inessive)



**sentence\_id** - sentence's id in the Estonian Reference Corpus (Eesti Keele Koondkorpus)



**head\_id** - id of the obliques' head verb in the Estonian Reference Corpus (Eesti Keele Koondkorpus)



**head\_loc1** - id of form1 in the sentence that the sentence\_id refers to



**head\_loc2** - id of form2 in the sentence that the sentence\_id refers to



**verb** - head verb of form1 and form2 that head\_id refers to



**verb\_compound** - the compound word of the obliques head verb when the head verb is a compound verb (ie astuma üles/step up - compound is üles/up)



**morph\_case1** - spatial case that form1 is in

* **abl** - ablative case (alaltütlev)
* **ad** - adessive case (alalütlev) 
* **adit** - additive case (lühike sisseütlev)
* **all** - allative case (alaleütlev)
* **el** - elative case (seestütlev)
* **ill** - illative case (pikk sisseütlev)
* **in** - inessive case (seesütlev)



**morph\_case2** - spatial case that form2 is in 

* **abl** - ablative case (alaltütlev)
* **ad** - adessive case (alalütlev)
* **adit** - additive case (lühike sisseütlev)
* **all** - allative case (alaleütlev)
* **el** - elative case (seestütlev)
* **ill** - illative case (pikk sisseütlev)
* **in** - inessive case (seesütlev)



**form1 -** form of the verb's first direct oblique dependent in a spatial case. Case is shown in morph\_case1.



**form2** - form of the verb's second direct oblique dependent in a spatial case. Case is shown in morph\_case2. Form2 always comes after form1 in a sentence.



**sentence** - text of the sentence the verb and form1/for2 are from



**error** - is some part of the morphosyntactic analysis wrong

* **true**: the morphosyntactic analysis is wrong
* **false**: the morphosyntactic analysis is correct



**error\_type** - if there is an error, then which kind is it

* **case**: one of the two obliques was assigned the wrong case tag
* **construction**: the morphosyntax is correct, but one oblique got its case due to a construction, not because of the verb (ie. *sai **vastasest** rohkem punkte* -> *vastane* got the elative case because of the word *rohkem*, not because of the verb *saama*, but it is still correctly labeled as the verb's direct dependent)
* **morphology+syntax**: one of the two obliques was assigned a wrong case tag, which is why it now has the wrong syntactic dependent
* **pos**: one of the two obliques was assigned the wrong part of speech tag
* **spelling**: the text's writer misspelled a word, due to which it got the right tags but wasn't logical for the sentence as a whole.
* **syntax**: one of the two obliques has the wrong syntactic head
* **verb**: the obliques received the correct analysis, but their head verb didn't (wrong lemma or part of speech)
* **verbal**\_**idiom**: on of the obliques forms a verbal multiword expression with its head verb.



**form1\_sem/form2\_sem** - the semantic type of form1/form2 (verb's direct oblique dependent). NB! semantic type here means the semantic property of the word itself, not the semantic role it receives as part of a sentence

* **abstract**: abstract entities like systems, relations, attributes (põllundus, kasutus, maine)
* **alive**: living beings (people and animals)
* **amount**: units of measurement, quantities
* **event**: activities/events that have both a locational and temporal meaning
* **location**: physical places where something can be located (countries, areas, rooms, buildings, cardinal directions)
* **object**: physical concrete objects (furniture, utensils, bodyparts, documents etc)
* **organisation**: collections of people (companies, teams, governments etc) \*(NB! Locations and organisations are systematically polysemous - the same word inherently has both meanings (the organisation = the building the organisation is located). The annotation was based on the annotators opinion on which meaning of the word is more commonly used)
* **state**: condition at a certain point in time, general situation
* **time**: period or moment in time.



**form1\_adverbial/form2\_adverbial** - what type of adverbial form1/form2 (verb's direct oblique dependent) is in this sentence. Adverbial type categorisation is based on the book "Eesti keele süntaks" (Estonian Syntax) 2017 (editors Mati Erelt, Helle Metslang).



* **amount**\_**adverbial** (hulgamäärus) - Expresses amount, quantity, measurement or degree of the event expressed in the sentence
* **government**\_**adverbial** (sõltuvusmäärus) - A residual class for adverbial arguments that do not belong to any other type of adverbial. The meanings of the adverbial do not form a single class; the form and meaning of the adverbial depends on its head rather than on the meaning of the adverbial word itself.
* **instrument**\_**adverbial** (vahendimäärus) - The instrument an activity is done with
* **location**\_**adverbial** (kohamäärus) - Expresses the location of an action or event described in the sentence. Can be a source, location, goal, direction, or area.
* **manner**\_**adverbial** (viisimäärus) - Expresses the manner in which an action or process occurs.
* **owner**\_**adverbial** (valdajamäärus) - Typically expresses a living being in whose possession or ownership something is, comes into or originates from (owner, beneficiary, recipient, source)
* **reason**\_**adverbial** (põhjuslik määrus) - Express the reason, condition, aim or consequence of an event happening. Typically adjuncts.
* **state**\_**adverbial** (seisundimäärus) - Expresses the position or condition of the subject or object of a sentence, i.e. physical, psychological, familial, social, material, health related, or other state, as well as the state of nature and weather.
* **time**\_**adverbial** (ajamäärus) - Indicates the temporal parameters of the event expressed in the sentence - the time of the event, the beginning and end of the event, its duration and frequency.



**comment**: specification on error type or the annotator's subjective notes/opinions

