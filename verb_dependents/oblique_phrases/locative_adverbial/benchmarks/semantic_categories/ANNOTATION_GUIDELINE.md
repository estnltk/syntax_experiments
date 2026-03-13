**V1 gpt kohtade märgendamise alus: esialgne versioon testsetide jaoks**

Testsetidest on näitelaused, kus geograafilised kohad, objektid, organisatsioonid, sündmused, inimesed ja abstraktsed asjad on lause kontekstis kohad.


Kohad: 

* geo_loc: geograafilised kohad 
	* kohanimed: Bristol, Sepphoris
	* ehitised/äride füüsilised asukohad: pangamaja, multimeediastuudio, Kuku klubi, käisime arvutifirmas
	* alad, mille geograafiline asukoht on defineeritav: põlengupaik, põhjapoolus, kaldapealne, tagaots, tolmupilv

* object_loc: objektid, mis võivad olla kohad 
	* füüsilised objektid: esikohapoodium, Kuu, varundusseade, sadul, pilv, põuetasku
	* kui väljendatakse abstraktset nähtust, aga objekti geograafiline asukoht on ikka määratav (nt hirm käib luust läbi - tegelikult pole hirm luus, aga luu on ise ikkagi kindla asukohaga)

* org_loc: organisatsioonid, mis võivad olla kohad 
	* organisatsioonid/kollektiivid: istun valitsuses, käin ülikoolis, hokitrennis, liigun võrgustikesse, lahkun töökohalt, vormelimaailm (koolid, trennid, lasteaiad)

* event_loc: tegevused/sündmused, millel on korraga nii aja kui koha tähendus
	* kleidiproov, värbamine, haldusmenetlus, prostitutsiooniprotsess, suusatreening 

* per_loc: inimene kui koht 
	* kui inimene ei ole kogeja/omaja/saaja/jne (nt "ema pani Peetrile teki peale" - Peeter ei ole kogeja vaid selles kontekstis on asukoht)

* abstract_loc: abstraktsed kohad, mille asukoht on kas ebamäärane või ei eksisteerigi
	* ebamäärased suunad/teekonnad: ida, trajektoor, liikus ummikteel 
	* nähtamatud/abstraktsed/määratlemata piirideta alad: Wifi, kvantmaailm, arvutiturg, õhuruum, digitaalplatvorm, liigub läheduses, hommikukaste, rambivalgus
	* veebisaidid, telekanalid: Delfi, Yle
	* abstraktsed mõisted: kirjanduses liiguvad väited, lahkusin poliitikast/võimult, kasutusaladel käib testimine
	* ülekantud tähendusega füüsiline liikumine: istus hooaja jooksul peatreeneripingile - sai peatreeneriks, istus lavastajapuldis - oli lavastaja



Mitte kohad, midagi muud, küsitavad, "ei oska öelda": 

* time: ajasõnad
	* kalendrilised ajad: aasta, hommik
	* perioodid: sügishooajal, elueas, tudengiajal

* owner: valdajamäärus (rüselejal käisid sussid, jooksid Markole amokki, käinud Aivarilt küsimas)

* state: seisund (jooksevad jalad rakku, käivad seelikus, liiguvad allhanke **pakkujast** maailmamajanduse juhtriigi poole, istun sitas, punktiarvestus käis kümnepallisüsteemis, elu käib tipptasandil)

* manner: viisimäärus (teravaimalt, käsikäes, omal hakatusel, korrelatsioonis)

* reason: põhjuslikud määrused (tagajärg, tingimus jne): hävitamisel, protsessori olemasolul, tagajärjel, tulemusel, mahitusel, hasardist

* other: rektsioonid ja stampväljendid
	* stampväljendid: üldjuhul, tulemusel, mõnes mõttes
	* konstruktsioon: vaatamata hoiakule, liigub kesklinlastest rohkem, käib jutt kehtivusest, linnapeadest käisid platsil Kõlvart ja Klaas, alates imikutest, üks haavlitest, astub loomale ligi, astub türklastest mööda, kohustuslikus/ettenähtud/ühiskondlikus korras, vastavalt vajadusele/seadusele/elukohale

* error: 
	* lemmatiseerimisviga (enne jõule -> jõud, Meriväljal -> meriväli)
	* arusaamatu sõna/kontekst (iimi -> 'iimist power lahkub', astub korda üles linal)
	* kirjaviga (kultuurikolledõisse)
	* süntaksiviga (sinisesse fordi - sinine pole amod vaid obl)
	

