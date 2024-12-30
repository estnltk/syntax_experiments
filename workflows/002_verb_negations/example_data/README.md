### Example data

Väiksemal transaktsioonide hulgal jooksutatud töövoo tulemuseks saadud andmebaasid.
Lähteandmeteks on andmebaas *transactions.db*, mis koosneb ~300 transaktsioonist, mille hulgas on esindatud nii eitusvormi sisaldavad,
eitusvormi mitte-sisaldavad, olemasolevatele verbimustritele vastavad, kui ka neile mitte-vastavad transaktsioonid. Transaktsioonid pärinevad transaktsioonide andmebaasi versioonist *v32*.

Töövoo tulemusel saadakse andmebaasid *negation_matches.db*, *negative_transactions.db*, *positive_transactions.db* ning *neg_support.db*. Tulemuse saavutamiseks kasutatakse arenduse käigus saadud verbi eitusmustrite andmebaasi *neg_patterns.db*

Andmebaasid *neg_tables.db* ja *neg_patterns.db* on loodud arendusetapi käigus ning põhinevad algsel transaktsioonide andmebaasil (v32).