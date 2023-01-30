# Märgendusjuhend

## I. Lõppeesmärk 
Märgendamise lõppeesmärk on jagada laiendid lauses eemaldamise tulemuse järgi nelja kategooriasse: 

* seotud laiendid (`bound_entity`)
* eemaldatavad vabad laiendid (`free_entity`)
* sõnajärge muutvad vabad laiendid (`unnatural_sentences`) 
* valed laiendid (märgitud sõna pole laiend) (`incorrect_entity`)

Seotud laiendid on laiendid mille eemaldamine lausest muudab lause mõtet. 
Vabade laiendide eemadamine jätab lause mõtte samaks, kaovad vaid detailid näiteks kuidas või kus tegevus toimub. 
Enamasti on vabade ja seotud laiendite eristamine lihtne. On mõned erandid, mida me käsitleme põhjalikumalt allpool.


Näiteks on _lauasahtlisse_ eemaldatav vaba laiend lauses

> Tembeldagem meresõiduamet tavaliseks kirjakontoriks , kus isegi laevaõnnetus võib ununeda <u>**lauasahtlisse**</u> . 

sest selle eemaldamine ei muuda lause põhisisu ja alles jääb loomuliku sõnajärjega lause

> Tembeldagem meresõiduamet tavaliseks kirjakontoriks , kus isegi laevaõnnetus võib ununeda.

Samas võib vaba laiendi eemaldamine tuua kaasa vajaduse allesjäänud lause sõnajärge muuta. Näiteks on laiend _selle aja jooksul_ lauses 

> Ta tõdeb , et <u>**selle aja jooksul**</u> on tema publik kõvasti muutunud :

vaba laiend, kuid laiendi eemaldamisel tekib ebaloomuliku sõnajärjega lause  

> Ta tõdeb , et on tema publik kõvasti muutunud :

mille asemel tuleks kasutada ümberjärjestatud sõnajärjega lauset

> Ta tõdeb , et tema publik on kõvasti muutunud :

Meie töö kontekstis on oluline eristada vabasid laiendeid, mille eemaldamine sunnib muutma lause sõnajärge. 
Kuna sellised ebaloomuliku lausejärjega laused ei esine tavatekstides, siis selliste lausete kasutamine süntaksianalüsaatori treenimisel ja evalveerimisel pole otstarbekohane

**Teooria versus praktika**

Keeleteadus käsitleb vabade ja seotud laiendite teemat (M. Erelt, M. Metsalang. Eesti Keele Süntaks, 2017) palju täpsemat kui antud märgenduse saamiseks vaja on: 
> Seotud laiendid on tüüpjuhul süntaktiliselt obligatoorsed, vabad
laiendid fakultatiivsed. Siiski ei ole laiendi obligatoorsus või fakultatiivsus laiendi seotuse või vabaduse absoluutne näitaja. Komplement võib tihtipeale ära jääda verbist sõltumatutel põhjustel, näiteks indefiniitsena. Vrd Ta suitsetab sigaretti. – Ta suitsetab.
Teiselt poolt võib vaba laiend mõnikord olla obligatoorne. Nt
Ta käitub halvasti. – Ta käitub. Tal on paha tuju. – Tal on tuju.

Antud märgenduse loomise peaeesmärk on leida lühendatud laused, milles on lause süntaks sama kui originaalauses. Sealjuures on eristus vabadeks ja seotud laienditeks instrumentaalne. Absoluutne täpsus laiendite klassifitseerimisel pole oluline seni kuni lühendatud lause säilitab süntaksi. Loomulikult on korrektne kasulik, kuna võimaldab täpsemini uurida, millised seotud laiendid säilitavad süntaksi ja annab potentsiaalse võimaluse luua (reeglipõhiseid) automaatmärgendajaid. 

## II. Märgendusskeem

Praktilisel märgendamisel on otstarbekas vasta küsimustele

* Kas lühendatud lause on loomuliku sõnajärjega?
* Kas eemaldatav tekstifragment on laiend?
* Kas eemaldatav tekstifragment on vaba laiend?


## III. Iseloomulikud näited

### Eemaldatavad vabad laiendid

Laiend on vaba ja eemaldamisel jääb lause mõte piisavalt samaks ning ei teki ebaloomulikku sõnade järjekorda: 

> <u>**Minuga**</u> oleks võinud juhtuda midagi tõeliselt halba. <br/>
> Oleks võinud juhtuda midagi tõeliselt halba.

> <u>**Neile**<u> meie praegune haldusaparaat ei vasta. <br/>
> Meie praegune haldusaparaat ei vasta.

Kui esialgses lauses oli esimene sõna verb, siis laiendi eemaldamine ei tähenda tingimata ebaloomulikku sõnade järjekorda (vt sektsiooni "Sõnajärge muutvad vabad laiendid")

> Pöörab pilgu <u>**oma poegadele Jaanusele ( 17 ) ja Joosepile**<u> ning lisab , et tegelikult on patt öelda , et elu on raske. <br/>
> Pöörab pilgu ning lisab , et tegelikult on patt öelda , et elu on raske .


### Seotud laiendid

Laiend <u>**filmi**</u> on seotud verbivormiga <u>lõppedes</u> ja eemaldamisel muutub lause arusaamatuks:

> <u>**Filmi**</u> lõppedes jääb tunne , et unistus saab teoks. <br/>
> Lõppedes jääb tunne , et unistus saab teoks.

Laiend <u>**Suklesest**</u> on seotud verbiga <u>sai</u> eemaldamisel muutub lause arusaamatuks: :

> Haapsalu oli 1994. aastal , mil <u>**Suklesest**</u> sai Isamaa ja Liberaalide toel linnapea , mahajäänud linnake.</br>
> Haapsalu oli 1994. aastal , mil sai Isamaa ja Liberaalide toel linnapea , mahajäänud linnake.

Laiend <u>**kubismist**</u> on seotud verbivormiga <u>toodud</u> eemaldamisel muutub lause arusaamatuks: :

> Kretski ei kasutanud ära <u>**kubismist**</u> toodud kaasaegset pöörangut .</br>
> Kretski ei kasutanud ära toodud kaasaegset pöörangut .

Üldiselt on seotud laiend otseselt seotud verbi, mõne verbivormiga (nud, tud, des) või ühendverbiga. Tüüpilisemad näited antud märgenduste kontekstis on verbidega:

* kippuma, tikkuma;
* asuma, paiknema, peituma, jääma, jätma
* mahtuma, ulatuma

seotud kohalaiendid. Aga nende verbidega võivad olla seotud ka teist tüüpi laiendid. 

Oluline on märgata, et laiendi tüüpi ei mõjuta kontekstist lähtuv eeldatav lausestruktuur.
Laiend <u>**Tallinnas**</u> on vaba laiend hoolimata sellest, et lühendatud lause esimene osalause langeb stiilist välja:

> <u>**Tallinnas**</u> registreeriti 426 lapse sünd , Tartumaal 141 , Ida-Virumaal 138 , ... <br>
> Registreeriti 426 lapse sünd , Tartumaal 141 , Ida-Virumaal 138 , ... <br>


### Sõnajärge muutvad vabad laiendid 

Kuigi laiend on vaba, siis eemaldamisel tekib ebaloomulik sõnade järjekord:

> Ta tõdeb , et <u>**selle aja jooksul**</u> on tema publik kõvasti muutunud : <br/>
> Ta tõdeb , et on tema publik kõvasti muutunud :


> <u>**Sellel aastal**</u> tunnistas probleemi olemasolu 22% vastanutest , 78% eitas probleemi olemasolu. <br>
> Tunnistas probleemi olemasolu 22% vastanutest , 78% eitas probleemi olemasolu.

Paljudel juhtudel on ebaloomuliku sõnajärje tunnuseks verbi paiknemine lause või osaluse alguses lühendatud lauses:

> <u>**Mul**</u> on olnud võimalik mingeid situatsioone lihtsamalt lahendada . <br/>
> On olnud võimalik mingeid situatsioone lihtsamalt lahendada . <br/>

> Kuid <u>**Bureau Veritase puhul**</u> ei saa seda kuidagi teha .<br/>
> Kuid ei saa seda kuidagi teha .

Samas tekitavad mõned sellised siiski loomuliku lausejärjega lühendatud lauseid, kuigi lause sisu muutub täielikult: 

> <u>**Linnajuhtimisse**</u> on vaja värsket verd . </br>
> On vaja värsket verd .
 
> Miks sa kirjutad oma haigeid <u>**osakonnast**</u> välja nii kiiresti ? <br/>
> Miks sa kirjutad oma haigeid  välja nii kiiresti ? 

> Hinnavahe tekib <u>**tarbimiskoguste erinevuste tõttu**</u> . <br/>
> Hinnavahe tekib .
 
Kõik need on siiski vabad laiendid, kuigi lause mõte muutub üsna palju. 



### Ebakorrektsed laiendid

Siia lähevad süntaksi vigadest tingitud laiendite moodustamise vead. 
Üheks kõige tüüpilisemaks on kogu lause sisu märkimine laiendiks, mistõttu lühendatud lause on tühi:

> <u>**Laeva ehitamisel oli jämedalt eiratud konventsiooni Eluohutus Merel ( SOLAS ) esmanõudeid**</u>. <br/>
> .
