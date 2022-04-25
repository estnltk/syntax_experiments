# Manually labelled dataset

## I. Labelling instructions in Estonian

UD märgendus ei erista seotuid ja vabu määrsõnalised laiendeid.

|Laiendi tüüp| Näide|
|:----|:----|
| Vaba   | Lind laulab **ilusasti**.|
| Seotud | Ma suhtun sinusse **hästi**.|
| Vaba   | Ma armastan teda **rohkem kui kedagi teist.** ||
| Seotud | Ma suhtun sinusse **sama hästi kui kõigisse teistesse**.|

Seotud laiendite korral pole määrsõnalist laiendid võimalik lausest eemaldada
ilma lause sisu olulise muutumiseta. Tavaliselt on tulemuseks lause, mis ei näi
olevat isegi grammatiliselt korrektne. Lisaks sellele on olemas lauseid, kus
määrsõnaline laiend on lause mõtte jaoks nii olulisel kohal, et sellel on teine
UD märgend kui advmod.  

|Lause tüüp| Näide|
|:----|:----|
| Originaal | Ma suhtun sinusse **hästi**.|
| Lühendus  | Ma suhtun sinusse.|
| Originaal | Nad suhtuvad töösse **sama tõsiselt kui teised.** |
| Lühendus  | Nad suhtuvad töösse. |
| Originaal | Inimesi on **samapalju kui Rapla peol.** |
| Lühendus  | Inimesi on. |

Seega võib Stanza märgenduse põhjal tehtud automaatse lühenduse ebakorrektsus
olla põhjustatud kahest põhjusest:

* Seotud määrsünaline laiend on antud verbikonstruktsiooni puhul kohustuslik.
* Stanza on pannud määrsõnalisele laiendile ekslikult advmod märgendi.
* Stanza on leidnud määrsõnalise laiendi peasõna, kuid jätnud osa sõnu fraasi lisamata.

Kuna lühendatud laused on ebakorrektsed, siis suure tõenäosusega on pole nende
Stanza märgendus kooskõlaline originaallausetega. Sedatüüpi ebvakõlasid on lihtne leida.
Et ülesannet veelgi lihtsustada otsime me esmalt ainult selliseid  vigu Stanza
märgenduses, mille tulemuseks on ebakorreksed lühendused.

### Võrdluslaused

Eesmärgiks on tuvastada lausete lühendused, mille tulemusena tekivad ebakorrektsed
või muul moel imelikud laused. Lühendatud lause võib kaotada informatsiooni, aga
ta võiks eraldi võetuna olla mõistlik.


|Laused | Märgendus|
|:----|:----|
|Lind laulab **ilusasti**. <BR> Lind laulab.| Õige | 
|Ma suhtun sinusse **hästi**. <BR> Ma suhtun sinusse.| Vigane lause |
|Ma armastan teda **rohkem kui kedagi teist.** <BR> Ma armastan teda.| Õige |
|**Rohkem kui** kolmandik Tai 76 provintsist on kantud linnugripi riskitsooni. <BR> Kolmandik Tai 76 provintsist on kantud linnugripi riskitsooni.| Tähendus muutus |
|Selleks on **rohkem** kui kaalukas põhjus : **siis** jääb õppetöö kindlasti soiku. <BR> Selleks on kui kaalukas põhjus: jääb õppetöö soiku, on ta klassivenna näitel näinud.|Vigane lause|
|Mõni neist sai **rohkem kui teine.** <BR> Mõni neist sai. | Vigane lause|
|Teedele ja parkimiskohtadele jääb **niikuinii umbes** 15 protsenti maast. <BR> Teedele ja parkimiskohtadele jääb 15 protsenti maast. | Tähendus muutus |
|Tarmo Zernanti sõnul mõjutasid tudengid Tartu korteriturgu **rohkem kui kunagi varem.**<BR> Tarmo Zernanti sõnul mõjutasid tudengid Tartu korteriturgu. | Õige |
|Tarmo Zernanti sõnul mõjutasid tudengid **tänavu** Tartu korteriturgu **rohkem kui kunagi varem.**<BR> Tarmo Zernanti sõnul mõjutasid tudengid Tartu korteriturgu. | Tähendus muutus |
|Abilinnapea saatis kuu alguses **rohkem kui pooled eesti keele õpetajad** keeletaseme kontrolli. <BR> Abilinnapea saatis kuu alguses keeletaseme kontrolli. | Vigane lause|

Näidetest lähtuvalt võiks märgendada järgnevalt

1. Tuvastada ja eemaldada vormiliselt ebakorrektsed lühendused.
2. Tuvastada kas eemaldatud fraas on suurem kui ta olema peaks. 
3. Tuvastada kas lause tähendus muutus.

Lõpptulemusena võiks olla lausetepaaridel neli märgendit:

* Õige lühendus
* Liiga suur lühendus
* Tähenduse muutus
* Vigane lause 
