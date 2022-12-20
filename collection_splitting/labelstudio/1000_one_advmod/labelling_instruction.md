# Märgendusjuhend

## I. Lõppeesmärk 
Märgendamise lõppeesmärk on jagada laiendid lauses eemaldamise tulemuse järgi kolme kategooriasse: 

* seotud laiendid (`bound_entity`)
* eemaldatavad vabad laiendid (`free_entity`)
* sõnajärge muutvad vabad laiendid (`unnatural_sentences`) 

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

## II. Märgendusskeem

Praktilisel märgendamisel on otstarbekas vasta kõigepealt küsimusele

* Kas lühendatud lause on loomuliku sõnajärjega?

ja alles pärast seda tegeleda küsimustega

* Kas eemaldatav tekstifragment on laiend?
* Kas eemaldatav tekstifragment on vaba laiend?

> Kaire, kas me peaks seda peale suruma märgendusskeemiga?
> St näitama ainult lühendatud lauset ja küsima kas see on loomulik lause ja alles pärast küsima, kas loomulik lause on saadud vaba või seotud laiendi eemaldamisel.
> Või on efektiivsem vastata neile küsimustele korraga?  


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


### Sõnajärge muutvad vabad laiendid 

Kuigi laiend on vaba, siis eemaldamisel tekib ebaloomulik sõnade järjekord:

> <u>**Mullu**</u> kuulutas ajakiri People ta lahutatud lapsevanemate kategoorias musterisaks. <br/>
> Kuulutas ajakiri People ta lahutatud lapsevanemate kategoorias musterisaks.


>”<u>**Võib-olla**</u> on otsus ärijuhtimist tudeerima asuda mu alateadlik soov taganemisteed kindlustada,” arutleb Evelin. <br>
> ”On otsus ärijuhtimist tudeerima asuda mu alateadlik soov taganemisteed kindlustada,” arutleb Evelin.

### Ebakorrektsed laiendid

Siia lähevad süntaksi vigadest tingitud laiendite moodustamise vead.




