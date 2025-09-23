## Tag types
### Obliques in spatial cases
Obliques have 5 tags: alive, event, location, state, time. These have been combined from various ekilex semantic_type tags. 
If a word had several semantic types, then the word was considered under one semantic type if it had at least one tag from the list of that type's main tags and all other tags were in the main tag or accepted addition list.
  
* **location** (words that are locations with very high likelyhood): *'koht', 'koht_ala', 'koht_asutus', 'koht_geogr', 'koht_geogr_maailmajagu', 'koht_geogr_veekogu', 'koht_hoone', 'koht_kehaosa', 'koht_loodus', 'koht_suund/asend', 'abstr_asend/suund', 'ese_anum', 'omadus_koht'*
    * accepted addition: *ese_instru, ese, ese_kunst, ese_raha, ese_semio, ese_riie, taim, objekt_loodus, objekt, osa, nähtus_loodus*
* **time**: *'aeg', 'aeg_aastaaeg', 'aeg_kuu', 'aeg_nädalapäev', 'aeg_tähtpäev'*
    * accepted addition: *esitus, nähtus_loodus, omadus_aeg*
* **state**: *'seisund', 'seisund_haigus', 'seisund_füüs'*
    * accepted addition: *nähtus_psühh, nähtus, nähtus_loodus, omadus_psühh, abstr_asend/suund, abstr_konkr_omadus, ese_raha*
* **event**: *sündmus*
    * accepted addition: *tegevus, tegevus_tegu, ese_kunst, abstr/konkr, nähtus, toit, nähtus_füüs, tegevus_kõnetegu, tegevus_mäng*
* **not_location**: (words that can't be locations or can be locations very very rarely (such as people)): *ese_raha, ese_riie, esitus_arv, esitus_keel, esitus_keel_suhtlus, esitus_keel_täht, esitus_tiitel, esitus_tähis, in_elukutse, in_müt, in_omadus, in_rahvas, in_roll, in_tegija, amet, konkr_omadus, käsklus, loom_liik, loom_omadus, loom_putukas, nähtus_psühh, omadus, omadus_abstr, omadus_aeg, omadus_füüs, omadus_kval, omadus_psühh, tegevus_muutus, tegevus_tegu, omadus_füüs_värv*


### Adverbs
Adverbs have 6 tags: amount, general, location, manner, state, time. These have been combined from various ekilex semantic_type tags.

* **amount**: *Adv_aste*
    * accepted addition: *abstr/konkr, kogus*
* **general**: *ADV_modaalsus, ADV_põhjus*
    * accepted addition: *abstr, abstr/konkr*
* **location** : *ADV_koht, koht, koht_suund/asend, abstr_asend/suund*
    * accepted addition: *seisund*
* **manner**: *ADV_viis, ADV_tulemus*
* **state**: *ADV_seisund, seisund, seisund_füüs*
* **time**: *ADV_aeg, aeg*
    * accepted addition: *omadus_aeg*