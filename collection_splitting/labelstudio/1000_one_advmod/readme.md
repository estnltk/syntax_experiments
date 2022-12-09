
1000 advmodi näidet võeti 5000 tekstiga koondkorpusest, mis oli eraldi lausetena salvestatud.

Näited võeti käsuga:

collection.select().sample( 20, amount_type='PERCENTAGE', seed=12345 )

Selle põhjal saadi lausete text_id-d, kust filtreeriti välja laused, milles oli 1 advmod sees (st syntax_ignore_entity kihi pikkus oli 1).

Lauseid võeti järjest niikaua kuni saadi 1000.


Skriptis 3 on näidete protsendiks pandud 30, et tagada vähemalt 1000 näite olemasolu muude deprelite jaoks.

