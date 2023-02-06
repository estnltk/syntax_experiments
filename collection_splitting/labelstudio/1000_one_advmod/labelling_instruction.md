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

Näiteks on _piisavalt_ eemaldatav vaba laiend lauses

> Tähtis on omada <u>**piisavalt**</u> raha, et oleks mugav olla.

sest selle eemaldamine ei muuda lause põhisisu ja alles jääb loomuliku sõnajärjega lause

> Tähtis on omada raha, et oleks mugav olla.

Samas võib vaba laiendi eemaldamine tuua kaasa vajaduse allesjäänud lause sõnajärge muuta. Näiteks on laiend _mullu_ lauses 

> <u>**Mullu**</u> kuulutas ajakiri People ta lahutatud lapsevanemate kategoorias musterisaks.

vaba laiend, kuid laiendi eemaldamisel tekib ebaloomuliku sõnajärjega lause  

> Kuulutas ajakiri People ta lahutatud lapsevanemate kategoorias musterisaks.

mille asemel tuleks kasutada ümberjärjestatud sõnajärjega lauset

> Ajakiri People kuulutas ta lahutatud lapsevanemate kategoorias musterisaks.

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

> Tähtis on omada <u>**piisavalt**</u> raha, et oleks mugav olla. <br/>
> Tähtis on omada raha, et oleks mugav olla.

Kuigi lause sisu muutub jääb lause põhiolemus samaks -- me imestame tema iseloomu üle:

> On tal <u>**vast**</u> iseloom! <br/>
> On tal iseloom!


### Seotud laiendid

Laiend _ei_ on seotud ja eemaldamisel muutub lause arusaamatuks:

> <u>**Ei**</u> ühele ega teisele olnud laevahuku põhjus mingiks saladuseks. <br/>
> Ühele ega teisele olnud laevahuku põhjus mingiks saladuseks .

>Sünnipäeval tõukas keegi Anna <u>**pikali**</u> . <br/>
>Sünnipäeval tõukas keegi Anna .


### Sõnajärge muutvad vabad laiendid 

Kuigi laiend on vaba, siis eemaldamisel tekib ebaloomulik sõnade järjekord:

> <u>**Mullu**</u> kuulutas ajakiri People ta lahutatud lapsevanemate kategoorias musterisaks. <br/>
> Kuulutas ajakiri People ta lahutatud lapsevanemate kategoorias musterisaks.

>”<u>**Võib-olla**</u> on otsus ärijuhtimist tudeerima asuda mu alateadlik soov taganemisteed kindlustada,” arutleb Evelin. <br>
> ”On otsus ärijuhtimist tudeerima asuda mu alateadlik soov taganemisteed kindlustada,” arutleb Evelin.

Paljudel juhtudel on ebaloomuliku sõnajärje tunnuseks verbi paiknemine lause alguses. Selline olukord tekib juhtudel, kus eemaldatav sõna on lauses esimene. 

Samas tekitavad mõned sellised siiski loomuliku lausejärjega lühendatud lauseid: 

><u>**Samas**</u> tundub , et esimesed reformid olid instrumentaalsed esimese faasi tööjõuturu pöörde loomisel ja mõjutasid teist faasi vähem . <br/>
>Tundub , et esimesed reformid olid instrumentaalsed esimese faasi tööjõuturu pöörde loomisel ja mõjutasid teist faasi vähem .

><u>**Sestap**</u> alustan ja lõpetan aeglases tempos . <br/>
>Alustan ja lõpetan aeglases tempos .



### Ebakorrektsed laiendid

Siia lähevad süntaksi vigadest tingitud laiendite moodustamise vead. 
Üheks kõige tüüpilisemaks on kogu lause sisu märkimine laiendiks, mistõttu lühendatud lause on tühi.



### Üleliigse komaga või kirjavahemärgiga laiend

Mõnikord on laiendi vaba, kuid selle eemaldamisel jääb koma või muu kirjavahemärk lauses valesse kohta:

><u>**Näiteks**</u> : olen söögitoa akna juures või magamistoa keskel . <br/>
>: olen söögitoa akna juures või magamistoa keskel .

>Ja see hale vahendatud maailm tundub meile millegipärast olulisena , <u>**rohkem eluna kui elu**</u> . <br/>
>Ja see hale vahendatud maailm tundub meile millegipärast olulisena , .

Need tuleks vastavalt märgendada kas "redundant comma" või "other redundant punctuation".


### Küsitav (dubious)

Vahel võib olla lause konteksti teadmata raske märgendada laiendit vabaks/seotuks. 

Lausete märgendamine küsitavaks ei ole eelistatud variant ning see on mõeldud erijuhtudeks.

