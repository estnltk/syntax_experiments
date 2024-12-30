## Tabeli *patterns* puudused

Tabeli *patterns* puudused andmebaasis *vp_data3.db*

 - Juhud, kus lähteandmetes on olnud käände küsisõnaks *kuhu* on hetkel tabelis kõigil juhtudel määratud käändeks alaleütlev (all) tulenevalt küsisõnade-käänete mappingu iseärasustest. Vaja oleks tekitada mitmesus (et sobib nii alaleütlev, sisseütlev või lühike sisseütlev kääne) või määrata, et sobib ainult lühike sisseütlev kääne. Samas, kui hiljem otsida uusi mustreid apriori abil, saadakse ülejäänud võimalikud käändevariandid ikkagi kätte.
 - Hetkel on tabelis ainult mustrid, mille verbil on kuni 1 compound:prt.
 - Hetkel on tabelis ainult mustrid, mille koosseisu ei kuulu *other* kategooriasse kuuluv osa.
 - Hetkel ei kajasta mustri ID-d (*pat_id*) selle vastet kas *patterns_len1* või *patterns_len2* tabelites *verb_patterns_new.db* andmebaasis.
 - Nüüdseks on mustritabelisse lisatud ka kaheliikmelised mustrid, uueks andmebaasiks on *vp_data4.db*. Kuna aga muid tabeleid pole nende mustritega veel läbi jooksutatud, ei kajastu need edasises töövoos.