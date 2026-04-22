--QUERY 1: LEIA sõnad, millel on ainult üks semantiline tüüp ja see on adverbi oma
WITH words_with_target_types AS (
    SELECT DISTINCT w.value AS word
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    JOIN meaning m ON m.id = l.meaning_id 
    JOIN meaning_semantic_type mst ON m.id = mst.meaning_id 
    JOIN semantic_type st ON mst.semantic_type_code = st.code
    WHERE w.lang = 'est' 
    AND (
        st.code IN (
            'ADV_modaalsus', 'ADV_aeg', 'ADV_tulemus', 'ADV_seisund', 'ADV_aste', 'ADV_viis',
            'ADV_põhjus', 'ADV_koht'
        )
    )
),
--leia, mis semantiliste tüüpidega iga sõna on
word_semantic_types as (
SELECT w.value AS word, st.code AS semantic_types
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    JOIN meaning m ON m.id = l.meaning_id 
    JOIN meaning_semantic_type mst ON m.id = mst.meaning_id 
    JOIN semantic_type st ON mst.semantic_type_code = st.code
    WHERE w.value IN (SELECT word FROM words_with_target_types)  -- Limit to words found in Step 1
    GROUP BY w.value, st.code
    ),
word_type_counts AS (
    -- Count distinct semantic types per word
    SELECT word, COUNT(DISTINCT semantic_types) AS type_count
    FROM word_semantic_types
    GROUP BY word
)
SELECT count(wst.word)
FROM word_semantic_types wst
JOIN word_type_counts wtc ON wst.word = wtc.word
WHERE wtc.type_count = 1; -- Only keep words with 1 semantic type

--QUERY 2: LEIA KÕIK SÕNAD, MILLEL ON vähemalt üks adverbidele kuuluv semantiline tüüp
WITH words_with_target_types AS (
    SELECT DISTINCT w.value AS word
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    JOIN meaning m ON m.id = l.meaning_id 
    JOIN meaning_semantic_type mst ON m.id = mst.meaning_id 
    JOIN semantic_type st ON mst.semantic_type_code = st.code
    WHERE w.lang = 'est' 
    AND (
        st.code IN (
            'ADV_modaalsus', 'ADV_aeg', 'ADV_tulemus', 'ADV_seisund', 'ADV_aste', 'ADV_viis',
            'ADV_põhjus', 'ADV_koht'
        )
    )
)
SELECT count(w.value)
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    JOIN meaning m ON m.id = l.meaning_id 
    JOIN meaning_semantic_type mst ON m.id = mst.meaning_id 
    JOIN semantic_type st ON mst.semantic_type_code = st.code
    WHERE w.lang = 'est' and w.value IN (SELECT word FROM words_with_target_types)  -- Limit to words found in Step 1
    ;

--QUERY 3: LEIA KÕIK ADVERBID, MILLEL ON ÜKS VÕI MITU KOHAGA SOBIVAT MÄRGENDIT
WITH adverbs AS (
    SELECT DISTINCT w.value AS word
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    join lexeme_pos lp on lp.lexeme_id = l.id
    WHERE w.lang = 'est' 
    AND lp.pos_code = 'adv'
),
--võta ainult kohasõnad
kohad AS (
    SELECT DISTINCT w.value AS word
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    JOIN meaning m ON m.id = l.meaning_id 
    JOIN meaning_semantic_type mst ON m.id = mst.meaning_id 
    JOIN semantic_type st ON mst.semantic_type_code = st.code
    WHERE w.value IN (SELECT word FROM adverbs)  -- Limit to adverbs
    AND (
        st.code IN ('ADV_koht', 'koht', 'koht_suund/asend', 'abstr_asend/suund')
    )
),
--leia, mis semantiliste tüüpidega iga kohasõna on + grupeeri koht ja temaga sobivad märgendid
word_semantic_types as (
SELECT w.value AS word,
            CASE 
                WHEN st.code IN (
                    'ADV_koht', 'koht', 'koht_suund/asend', 'abstr_asend/suund') 
                    THEN 'KOHT'
                WHEN st.code IN (
                	'seisund') 
                    THEN 'SOBIB'
                ELSE 'OTHER' -- Keep other types as they are
            END
         AS semantic_types
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    JOIN meaning m ON m.id = l.meaning_id 
    JOIN meaning_semantic_type mst ON m.id = mst.meaning_id 
    JOIN semantic_type st ON mst.semantic_type_code = st.code
    WHERE w.value IN (SELECT word FROM kohad)  -- Limit to kohamärgendiga sõnad
    GROUP BY w.value, st.code
    ),
--Put each semantic tag class in a separate column
word_type_counts AS (
    SELECT word, 
           COUNT(DISTINCT semantic_types) AS type_count,
           BOOL_OR(semantic_types = 'KOHT') AS has_koht,
           BOOL_OR(semantic_types = 'SOBIB') AS has_sobib,
           BOOL_OR(semantic_types = 'OTHER') AS has_other
    FROM word_semantic_types
    GROUP BY word
)
--vali sellised sõnad, millel on kas 1. üks semantiline tüüp ja see on koht või 2. kaks semantilist tüüpi ja need on koht ja sobib
SELECT 
    wtc.word
FROM word_type_counts wtc
WHERE (
    (wtc.type_count = 1 AND wtc.has_koht)  -- If 1 type, it must be koht
    OR
    (wtc.type_count = 2 AND wtc.has_koht AND wtc.has_sobib)  -- If 2 types, must be koht and SOBIB
)
ORDER BY wtc.word;

--QUERY 4: LEIA KÕIK ADVERBID, MILLEL ON ÜKS VÕI MITU AJAGA SOBIVAT MÄRGENDIT
WITH adverbs AS (
    SELECT DISTINCT w.value AS word
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    join lexeme_pos lp on lp.lexeme_id = l.id
    WHERE w.lang = 'est' 
    AND lp.pos_code = 'adv'
),
--võta ainult kohasõnad
ajad AS (
    SELECT DISTINCT w.value AS word
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    JOIN meaning m ON m.id = l.meaning_id 
    JOIN meaning_semantic_type mst ON m.id = mst.meaning_id 
    JOIN semantic_type st ON mst.semantic_type_code = st.code
    WHERE w.value IN (SELECT word FROM adverbs) 
    AND (
        st.code IN ('ADV_aeg', 'aeg')
    )
),
--leia, mis semantiliste tüüpidega iga kohasõna on + grupeeri koht ja temaga sobivad märgendid
word_semantic_types as (
SELECT w.value AS word,
            CASE 
                WHEN st.code IN ('ADV_aeg', 'aeg') 
                    THEN 'AEG'
                WHEN st.code IN ('omadus_aeg') 
                    THEN 'SOBIB'
                ELSE 'OTHER'
            END
         AS semantic_types
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    JOIN meaning m ON m.id = l.meaning_id 
    JOIN meaning_semantic_type mst ON m.id = mst.meaning_id 
    JOIN semantic_type st ON mst.semantic_type_code = st.code
    WHERE w.value IN (SELECT word FROM ajad)  -- Limit to words found in Step 1
    GROUP BY w.value, st.code
    ),
--Put each semantic tag class in a separate column
word_type_counts AS (
    SELECT word, 
           COUNT(DISTINCT semantic_types) AS type_count,
           BOOL_OR(semantic_types = 'AEG') AS has_aeg,
           BOOL_OR(semantic_types = 'SOBIB') AS has_sobib,
           BOOL_OR(semantic_types = 'OTHER') AS has_other
    FROM word_semantic_types
    GROUP BY word
)
--vali sellised sõnad, millel on kas 1. üks semantiline tüüp ja see on aeg või 2. kaks semantilist tüüpi ja need on aeg ja sobib
SELECT 
    wtc.word
FROM word_type_counts wtc
WHERE (
    (wtc.type_count = 1 AND wtc.has_aeg)  -- If 1 type, it must be AEG
    OR
    (wtc.type_count = 2 AND wtc.has_aeg AND wtc.has_sobib)  -- If 2 types, must be AEG and SOBIB
)
ORDER BY wtc.word;

--QUERY 5: LEIA KÕIK ADVERBID, MILLEL ON ÜKS VÕI MITU ÜLDLAIENDIGA SOBIVAT MÄRGENDIT
WITH adverbs AS (
    SELECT DISTINCT w.value AS word
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    join lexeme_pos lp on lp.lexeme_id = l.id
    WHERE w.lang = 'est' 
    AND lp.pos_code = 'adv'
),
--võta ainult kohasõnad
yldlaiend AS (
    SELECT DISTINCT w.value AS word
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    JOIN meaning m ON m.id = l.meaning_id 
    JOIN meaning_semantic_type mst ON m.id = mst.meaning_id 
    JOIN semantic_type st ON mst.semantic_type_code = st.code
    WHERE w.value IN (SELECT word FROM adverbs) 
    AND (
        st.code IN ('ADV_modaalsus', 'ADV_põhjus')
    )
),
--leia, mis semantiliste tüüpidega iga kohasõna on + grupeeri koht ja temaga sobivad märgendid
word_semantic_types as (
SELECT w.value AS word,
            CASE 
                WHEN st.code IN ('ADV_modaalsus', 'ADV_põhjus') 
                    THEN 'YLD'
                WHEN st.code IN ('abstr', 'abstr_konkr') 
                    THEN 'SOBIB'
                ELSE 'OTHER'
            END
         AS semantic_types
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    JOIN meaning m ON m.id = l.meaning_id 
    JOIN meaning_semantic_type mst ON m.id = mst.meaning_id 
    JOIN semantic_type st ON mst.semantic_type_code = st.code
    WHERE w.value IN (SELECT word FROM yldlaiend)  -- Limit to words found in Step 1
    GROUP BY w.value, st.code
    ),
--Put each semantic tag class in a separate column
word_type_counts AS (
    SELECT word, 
           COUNT(DISTINCT semantic_types) AS type_count,
           BOOL_OR(semantic_types = 'YLD') AS has_yld,
           BOOL_OR(semantic_types = 'SOBIB') AS has_sobib,
           BOOL_OR(semantic_types = 'OTHER') AS has_other
    FROM word_semantic_types
    GROUP BY word
)
--vali sellised sõnad, millel on kas 1. üks semantiline tüüp ja see on aeg või 2. kaks semantilist tüüpi ja need on aeg ja sobib
SELECT 
    wtc.word
FROM word_type_counts wtc
WHERE (
    (wtc.type_count = 1 AND wtc.has_yld)  -- If 1 type, it must be AEG
    OR
    (wtc.type_count = 2 AND wtc.has_yld AND wtc.has_sobib)  -- If 2 types, must be AEG and SOBIB
)
ORDER BY wtc.word;

--QUERY 6: LEIA KÕIK ADVERBID, MILLEL ON ÜKS VÕI MITU VIISIGA SOBIVAT MÄRGENDIT
WITH adverbs AS (
    SELECT DISTINCT w.value AS word
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    join lexeme_pos lp on lp.lexeme_id = l.id
    WHERE w.lang = 'est' 
    AND lp.pos_code = 'adv'
),
--võta ainult viisisõnad
viis AS (
    SELECT DISTINCT w.value AS word
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    JOIN meaning m ON m.id = l.meaning_id 
    JOIN meaning_semantic_type mst ON m.id = mst.meaning_id 
    JOIN semantic_type st ON mst.semantic_type_code = st.code
    WHERE w.value IN (SELECT word FROM adverbs) 
    AND (
        st.code IN ('ADV_viis', 'ADV_tulemus')
    )
),
--leia, mis semantiliste tüüpidega iga kohasõna on + grupeeri koht ja temaga sobivad märgendid
word_semantic_types as (
SELECT w.value AS word,
            CASE 
                WHEN st.code IN ('ADV_viis', 'ADV_tulemus') 
                    THEN 'VIIS'
                ELSE 'OTHER'
            END
         AS semantic_types
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    JOIN meaning m ON m.id = l.meaning_id 
    JOIN meaning_semantic_type mst ON m.id = mst.meaning_id 
    JOIN semantic_type st ON mst.semantic_type_code = st.code
    WHERE w.value IN (SELECT word FROM viis)  -- Limit to words found in Step 1
    GROUP BY w.value, st.code
    ),
--Put each semantic tag class in a separate column
word_type_counts AS (
    SELECT word, 
           COUNT(DISTINCT semantic_types) AS type_count,
           BOOL_OR(semantic_types = 'VIIS') AS has_viis,
           BOOL_OR(semantic_types = 'OTHER') AS has_other
    FROM word_semantic_types
    GROUP BY word
)
--vali sellised sõnad, millel on kas 1. üks semantiline tüüp ja see on aeg või 2. kaks semantilist tüüpi ja need on aeg ja sobib
SELECT 
    wtc.word
FROM word_type_counts wtc
WHERE (wtc.type_count = 1 AND wtc.has_viis)  -- If 1 type, it must be VIIS
ORDER BY wtc.word;

--QUERY 7: LEIA KÕIK ADVERBID, MILLEL ON ÜKS VÕI MITU HULGAGA/ASTMEGA SOBIVAT MÄRGENDIT
WITH adverbs AS (
    SELECT DISTINCT w.value AS word
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    join lexeme_pos lp on lp.lexeme_id = l.id
    WHERE w.lang = 'est' 
    AND lp.pos_code = 'adv'
),
--võta ainult hulgasõnad
hulk AS (
    SELECT DISTINCT w.value AS word
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    JOIN meaning m ON m.id = l.meaning_id 
    JOIN meaning_semantic_type mst ON m.id = mst.meaning_id 
    JOIN semantic_type st ON mst.semantic_type_code = st.code
    WHERE w.value IN (SELECT word FROM adverbs) 
    AND (
        st.code IN ('ADV_aste')
    )
),
--leia, mis semantiliste tüüpidega iga hulgasõna on + grupeeri hulk ja temaga sobivad märgendid
word_semantic_types as (
SELECT w.value AS word,
            CASE 
                WHEN st.code IN ('ADV_aste') 
                    THEN 'ASTE'
                WHEN st.code IN ('abstr/konkr', 'kogus') 
                    THEN 'SOBIB'
                ELSE 'OTHER'
            END
         AS semantic_types
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    JOIN meaning m ON m.id = l.meaning_id 
    JOIN meaning_semantic_type mst ON m.id = mst.meaning_id 
    JOIN semantic_type st ON mst.semantic_type_code = st.code
    WHERE w.value IN (SELECT word FROM hulk)  -- Limit to words found in Step 1
    GROUP BY w.value, st.code
    ),
--Put each semantic tag class in a separate column
word_type_counts AS (
    SELECT word, 
           COUNT(DISTINCT semantic_types) AS type_count,
           BOOL_OR(semantic_types = 'ASTE') AS has_aste,
           BOOL_OR(semantic_types = 'SOBIB') AS has_sobib,
           BOOL_OR(semantic_types = 'OTHER') AS has_other
    FROM word_semantic_types
    GROUP BY word
)
--vali sellised sõnad, millel on kas 1. üks semantiline tüüp ja see on aste või 
--2. kaks semantilist tüüpi ja need on aste ja sobib
SELECT 
    wtc.word
FROM word_type_counts wtc
WHERE (
    (wtc.type_count = 1 AND wtc.has_aste)  -- If 1 type, it must be ASTE
    OR
    (wtc.type_count = 2 AND wtc.has_aste AND wtc.has_sobib)  -- If 2 types, must be aste and SOBIB
)
ORDER BY wtc.word;

--QUERY 8: LEIA KÕIK ADVERBID, MILLEL ON ÜKS VÕI MITU SEISUNDIGA SOBIVAT MÄRGENDIT
WITH adverbs AS (
    SELECT DISTINCT w.value AS word
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    join lexeme_pos lp on lp.lexeme_id = l.id
    WHERE w.lang = 'est' 
    AND lp.pos_code = 'adv'
),
--võta ainult seisundisõnad
seisund AS (
    SELECT DISTINCT w.value AS word
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    JOIN meaning m ON m.id = l.meaning_id 
    JOIN meaning_semantic_type mst ON m.id = mst.meaning_id 
    JOIN semantic_type st ON mst.semantic_type_code = st.code
    WHERE w.value IN (SELECT word FROM adverbs) 
    AND (
        st.code IN ('ADV_seisund', 'seisund', 'seisund_füüs')
    )
),
--leia, mis semantiliste tüüpidega iga seisund on + grupeeri seisund ja temaga sobivad märgendid
word_semantic_types as (
SELECT w.value AS word,
            CASE 
                WHEN st.code IN ('ADV_seisund', 'seisund', 'seisund_füüs') 
                    THEN 'SEISUND'
                ELSE 'OTHER'
            END
         AS semantic_types
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    JOIN meaning m ON m.id = l.meaning_id 
    JOIN meaning_semantic_type mst ON m.id = mst.meaning_id 
    JOIN semantic_type st ON mst.semantic_type_code = st.code
    WHERE w.value IN (SELECT word FROM seisund)  -- Limit to words found in Step 1
    GROUP BY w.value, st.code
    ),
--Put each semantic tag class in a separate column
word_type_counts AS (
    SELECT word, 
           COUNT(DISTINCT semantic_types) AS type_count,
           BOOL_OR(semantic_types = 'SEISUND') AS has_seisund,
           BOOL_OR(semantic_types = 'OTHER') AS has_other
    FROM word_semantic_types
    GROUP BY word
)
--vali sellised sõnad, millel on kas 1. üks semantiline tüüp ja see on seisund või 
--2. kaks semantilist tüüpi ja need on seisund ja sobib
SELECT 
    wtc.word
FROM word_type_counts wtc
WHERE (
    (wtc.type_count = 1 AND wtc.has_seisund)  -- If 1 type, it must be seisund
)
ORDER BY wtc.word;