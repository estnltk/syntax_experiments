# Veel näited kohakäändes olevate sõnade märgendamisel tekkinud probleemidest

### morf analüsaatori huvitavad valikud:
	- levitama + elukas: Peale selle , et paljude inimeste jaoks on rott vastik , levitab elukas kõikvõimalikke haigusi .
	
	morph_analysis: ('elukas', 'sg n', 'S'), ('elukas', 'sg in', 'S')

	->Mõlemad analüüsid teoreetiliselt võimalikud, inessiivis analüüsi puhul koht
	
	- ilutsema + abielus (in): Eriti just viimasest , sest kui Kreitzbergi passis peaks olema perekonnaseisu kohta tempel " lahutatud " , siis tema elukaaslasel Sirje Priimäel ilutseb seal " abielus " .
	
	morph_analysis: ('abi_elu', 'sg in', 'S')

	-> morfo ja süntaks tegelt õiged, lihtsalt imelikud, sest see on keeruline lause.

	- jooksma + joonisfilmidele: Mitmele teisele stuudiole on ühtäkki tulnud mõte , et ka nemad võiksid saada osa neist tohututest summadest , mis seni tänu joonisfilmidele on jooksnud Disney rahakirstudesse .
	
	joonisfilmidele ja rahakirstudesse on mõlemad "jooksma" alluvad 

	-> Kaassõna rektsioon, vaadata järgi mis kaassõnad tahavad kohakäändeid. Võtta sellised kaassõnafraasid sealt tekstist välja.
		
	Pole peasõnaga seotud aga kummaline:

	- Sellegipoolest töötasid eelmisel aastal kokku 659 Tallinna noort vanuses 13-18 aastat 34 linnasiseses ja üheksas linnavälises rühmas .

		"rühmas" morf analüüs annab ('rühm', 'sg in', 'S'), ('rühmama', 's', 'V')

		stanza ütleb: rühmas on rühmama verb ja allus sõnale "töötasid" (mis on ka verb ja root)

	-> Morfoviga

### ühildumine: (eelnev/järgnev sõna on eraldi reana transaction_row tabelis; praegu 57 juhtu 1300st; ill=adit)

	- kulgema + hallilt : Kohtumine kulges tavapäraselt hallilt .
	
	- sõitma + ebaikainelt: Ebakainena on roolis olnud 37 protsenti juhtidest , rohkem kui üks protsent kõigist juhtidest sõidab aga pidevalt ebakainelt .
	
	-> peavadki eraldi obliikva olema. Siin tuleb teha fraasitest: kas saab lauses lahku tõsta

	- esitlema + alkoholijoobes: Omanikuna esitles end alkoholijoobes mees , kes politsei pressiesindaja sõnul solvas politseinikke , öeldes , et märgikandjad on viimased , keda ta oma baaris näha tahab .
	
	- magama + joobes (lemma=joove): 25.jaanuaril kell 22.20 magas joobes mees Maardus Keemikute tänaval		
	
		(mees: analüüs annab nii 'mees' (ilma kohakäändeta) kui ka 'mesi' (kohakäändega), ühildumisel on see tuvastatud kuna üks analüüsi variant sisaldab kohakäänet)
	
	- helisema + ärevuses: Tulge ruttu kohale , " helises eile kell 12 . 48 Pärnumaa häirekeskuses ärevuses telefon .

	-> sinises sõnad peaks olema subjekti täiendid, nmod.

	- ronima + räägi (lemma=rääkima): staff: kassnaine krt roni privasse räägi oma murest siis

	-> morfoviga

	- mahtuma + laiustesse: Seattleis tuli kohaliku praamiliini laevadel istekohad välja vahetada pärast reisijate kaebusi , et nad ei mahu 45 sentimeetri laiustesse toolidesse ära .

	-> süntaksiviga, laiustesse sõnal on vale pea, peaks olema toolidesse

	- paiknema(ad)+haigetel: Sellele võib lihtsalt vastata , väites , et need , kelle raamatutest ning ideedest oli äsja juttu , paiknevad Lääne pühiskonna psüühiliselt haigetel äärealadel .

	-> süntaksiviga, haigetel sõnal on vale pea, õige äärealadel
		
	- rändama + kahekuulist(lemma=kahekuul): Septembri algul rändas viis last pärast kahekuulist eri peredes veedetud suve lastekodusse .

	->vale morfo, pärast lemma = pära. Päris laiend on kaugel (suve)

	- jõudma + 25 000-sse : STV pakutavad kanalid jõuavad 25 000-sse koju . (ill vs adit; number ja "koju" on "jõudma" alluvad)

	-> vale süntaks, 25000sse allub kojule tegelt


	- lamama + igal: Üks pealtnägija rääkis BBCle , et nägi , kuidas kahekordne buss oli lõhki nagu " karp sardiine " ning inimesi lamas igal pool .
	
	morph_analysis: igal (ad, P), pool (puudub kohakääne, K)
		
	stanza: "igal" (det) allub "pool" (obl) ja ’pool’ on ’lamas’ alluv
   
	-> Süntaksiviga, igal pool peaks kokku käima.

### viisimäärus:
	- paiknema + alusel: Edetabelikohtade summa alusel paikneb Eesti 17 naiskonna konkurentsis 13. kohal .
	
	(alusel, ettekäändel, kaalutlustel, hinnangul, kujul jne )

	-> Siirdemäärus, eraldi konstruktsioon

	- paigutama + seadusele: Direktori närv ei pidanud vastu ja ta paigutas nad vastavalt täitevmenetluse seadusele karantiiniosakonda .

	-> vastavalt määrsõna rektsioon -> vastavalt millele. Põhjuslik määrus.

#### vaatamata millelegi:
	
	- jooksma + jalgadele: Kuidas asjad vanasti käisid Kui Intsikurmu volbriööl maha põletati , jooksis Aleksander ( aastakümneid Põlvamaal kindlakäeliselt kultuurielu suunanud Kinuneni Sass ) hommikul haigetele jalgadele vaatamata üle Põlva küngaste jubedust oma silmaga kaema .
		
	- investeerima+olukorrale: Roosaare sõnul investeerib Toom Tekstiil maailmaturu pingelisele olukorrale vaatamata endiselt vähemalt miljon krooni kuus .

	-> kaassõna\mata-vormi rektsioon vaatamata millele. Põhjuslik määrus. 


	- sõitma + kõrguselt: 7. juulil sõitis Koluvere sillalt nelja meetri kõrguselt jõkke 30 aastat vana Volvo-buss .
		
	morph_analysis: ('kõrgune', 'sg abl', 'A'),('kõrgus', 'sg abl', 'S'),('kõrguse=lt', '', 'D')
		
	stanza: "kõrguselt" ja "sillalt" on "sõitma" alluvad

	-> Sillalt on kohamäärus, kõrguselt on hulgamääras. Analüüs õige.


### MILLEST MIS:
	- varastama + kaitseliitlasest: Poolesajal kaitseliitlasel , politseinikul ja päästeametnikul ei õnnestunud läinud nädala lõpuks leida Jõhvi lähedastest metsadest 23-aastast neiut , kes varastas kasuõe kaitseliitlasest mehelt püstoli ja lubas end tappa .
	
	’kaitseliitlasest’ ja ’mees’ on mõlemad ’varastama’ alluvad
	
	analyze_token: {'root': 'kaitse_liitlane',
  			'root_tokens': 'kaitse', 'liitlane',
  			'ending': 'st',
  			'clitic': '',
  			'partofspeech': 'S',
  			'form': 'sg el',
  			'lemma': 'kaitseliitlane'}

	->  sellele on lahendus olemas

numbrid:
- kerkima + -le: Inflatsioon on viimased kolm aastat olnud üle 6% ning kerkis tänavu juunis juba 8,8% -le .

->suure tõenäosusega on selline -le hulgamäärus, sest nii käänatakse tavaliselt numbreid.

- saama + 15sse: Maaliit sai 15sse ja Isamaaliit 14sse volikokku .

-> süntaksiviga

- paistma + 14-selt: Tänaseks 204 cm pikkune mees ei paistnud 14-selt veel sugugi silma , kuid peatselt " viskas " poolteise aastaga 20 sentimeetrit juurde .

-> määrsõna, peaks olema advmod

- lahkuma + 17liikmelisest: Aga kui 17liikmelisest lahkuvad pooled , siis võib probleem tekkida , " peab ta silmas poja tegevust koduteatris .

-> Õige süntaks

=> numbrid, millel on küljes käändelõpp, tuleks eraldi tõsta ja eraldi analüüsida.
		
### v-kesksõna 

- pakutama + tunnis: Töötule või sada krooni päevas teenivale inimesele on ühes tunnis pakutavad 140 krooni korralik teenistus .

 {'root': 'pakuta','root_tokens': ['pakuta'],'ending': 'vad','clitic': '','partofspeech': 'V', 'form': 'vad', 'lemma': 'pakutama'},

 {'root': 'pakutav', 'root_tokens': ['pakutav'], 'ending': 'd', 'clitic': '', 'partofspeech': 'A', 'form': 'pl n','lemma': 'pakutav'}

->  Morfoviga, pakutav mitmus



