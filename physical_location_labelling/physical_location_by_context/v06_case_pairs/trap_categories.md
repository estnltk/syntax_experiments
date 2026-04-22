## Märgendid ja nende N80 grupi verbide näited

* **TIME** = EKILEX TIME + TIMEX - heaks kiitma MILLAL (esmaspäeval), tagasi jõudma MILLAL (reedel), jõustuma MIS AJAST (aprillikuust), avalikustama MILLAL (esmaspäeval), saabuma MILLAL (aastavahetusel)
* **LOC** = EKILEX LOC + NER LOC - reisima KUHU (Aafrikasse), helistama KUHU (Afganistani), suunduma KUHU, sõitma KUHU, seadma sisse KUS (Ameerikas)
* **EVENT** =  EKILEX EVENT - osa võtma MILLEST (kunstimüügist, viktoriinist, laagrist), osalema MILLEL (valimistel, missioonil, konverentsil; TIME ja LOC on vabad laiendid (osalema sügisel Loksal valimistel)) (16 korda 118st esinemisest minu käsitsi andmestikus oli event sõltuvusmäärus, 84 korda kohamäärus, 12 korda ajamäärus millest 3 ei saanud lisaks ka kohana mõista)
* **STATE** = EKILEX STATE - haigestuma MILLESSE (tüüfusesse), kosuma MILLEST (gripist), nakatuma MILLESSE (grippi)
* **OWNER** = EKILEX ALIVE + NER PER - lahku minema KELLEST (peikast), tegema välja KELLELE (Ansipile), saama KELLELT (Jaanilt)
* **ORG** = NER ORG + **EKILEX koht_asutus ja grupp?** - Kontrollisin oma käsitsi märgendust, organisatsioon on valdaja 36 juhul ja koht 50 juhul.

## KOMBINATSIOONID ja nende N80 grupi verbide näited

* LOC + EVENT - sattuma MILLESSE (avariisse, Tartusse), tooma KUST (välisreisidelt, Tartust) jne
* TIME + EVENT - maha jääma MILLAL (tuppatulekul/reedel)
* TIME + LOC + EVENT - jõudma MILLAL/KUS (tegudeni jõutakse esmaspäeval/metsaveerel/istungil), varisema põrmu MILLAL/KUS (märtsis/stardis/Tartus)
* ORG + EVENT + ALIVE\PER + LOC - kuulma MILLEST (Kreisiraadiost, topingupruukimisest, kurjast mehest, linnast nimega Lamont Missouris) vrd kuulma KUST (koridorist samme, raadiost muusikat)

## LÕPLIKUD MÄRGENDIKOMBINATSIOONID

* KOHT = EKILEX location NER LOC + EKILEX organisation sisekohakäänetes + NER ORG sisekohakäänetes + EKILEX event
* SÜNDMUS = EKILEX event (kohast ka eraldi minu lingvistiliseks huviks)
* AEG = EKILEX time + TIMEX
* VABA LAIEND = KOHT + AEG
* VALDAJA = EKILEX alive + NER PER + EKILEX organisation väliskohakäänetes + NER ORG väliskohakäänetes 
* SEISUND = EKILEX state
