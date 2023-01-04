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



### Seotud laiendid

Laiend _filmi_ on seotud ja eemaldamisel muutub lause arusaamatuks:

> <u>**Filmi**</u> lõppedes jääb tunne , et unistus saab teoks. <br/>
> Lõppedes jääb tunne , et unistus saab teoks.


### Sõnajärge muutvad vabad laiendid 

Kuigi laiend on vaba, siis eemaldamisel tekib ebaloomulik sõnade järjekord:

> Ta tõdeb , et <u>**selle aja jooksul**</u> on tema publik kõvasti muutunud : <br/>
> Ta tõdeb , et on tema publik kõvasti muutunud :


> <u>**Sellel aastal**</u> tunnistas probleemi olemasolu 22% vastanutest , 78% eitas probleemi olemasolu. <br>
> Tunnistas probleemi olemasolu 22% vastanutest , 78% eitas probleemi olemasolu.

### Ebakorrektsed laiendid

Siia lähevad süntaksi vigadest tingitud laiendite moodustamise vead.

> <u>**Laeva ehitamisel oli jämedalt eiratud konventsiooni Eluohutus Merel ( SOLAS ) esmanõudeid**</u>. <br>
> .

> <u>**ta heaks , aga ootab tulemust .**</u> <br>
> 

