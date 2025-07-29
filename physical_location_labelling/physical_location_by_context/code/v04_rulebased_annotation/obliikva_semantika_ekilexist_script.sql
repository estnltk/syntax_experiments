--QUERY 1: LEIA KÕIK SÕNAD, MILLEL ON VÄHEMALT 1 KOHA/AJA/SEISUNDI/SÜNDMUSE TÄHENDUS 
--JA SÕNA KÕIK SEMANTILISED TÜÜBID
--võta ainult koha, aja, seisundi ja sündmuse sõnad
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
            'koht', 'koht_ala', 'koht_asutus', 'koht_geogr', 'koht_geogr_maailmajagu', 'koht_geogr_veekogu',
            'koht_hoone', 'koht_kehaosa', 'koht_loodus', 'koht_suund/asend', 'abstr_asend/suund', 'ese_anum', 'omadus_koht'
            'aeg', 'aeg_aastaaeg', 'aeg_kuu', 'aeg_nädalapäev', 'aeg_tähtpäev',
            'seisund', 'seisund_haigus', 'seisund_füüs',
            'sündmus'
        )
    )
),
--leia, mis semantiliste tüüpidega iga sõna on + grupeeri koht, aeg, seisund
word_semantic_types as (
SELECT w.value AS word,
            CASE 
                WHEN st.code IN (
                    'koht', 'koht_ala', 'koht_asutus', 'koht_geogr', 'koht_geogr_maailmajagu', 'koht_geogr_veekogu',
                    'koht_hoone', 'koht_kehaosa', 'koht_loodus', 'koht_suund/asend', 'abstr_asend/suund', 'ese_anum', 'omadus_koht') 
                    THEN 'KOHT'
                WHEN st.code IN ('aeg', 'aeg_aastaaeg', 'aeg_kuu', 'aeg_nädalapäev', 'aeg_tähtpäev') 
                    THEN 'AEG'
                WHEN st.code IN ('seisund', 'seisund_haigus', 'seisund_füüs') 
                    THEN 'SEISUND'
                ELSE st.code  -- Keep other types as they are
            END
         AS semantic_types
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    JOIN meaning m ON m.id = l.meaning_id 
    JOIN meaning_semantic_type mst ON m.id = mst.meaning_id 
    JOIN semantic_type st ON mst.semantic_type_code = st.code
    WHERE w.value IN (SELECT word FROM words_with_target_types)  -- Limit to words found in Step 1
    GROUP BY w.value, st.code
    )
--grupeeri semantilised tüübid sõna alla
SELECT wst.word,
    MAX(CASE WHEN wst.semantic_types = 'KOHT' THEN 'koht' END) AS koht,
    MAX(CASE WHEN wst.semantic_types = 'AEG' THEN 'aeg' END) AS aeg,
    MAX(CASE WHEN wst.semantic_types = 'SEISUND' THEN 'seisund' END) AS seisund,
    MAX(CASE WHEN wst.semantic_types = 'sündmus' THEN 'sündmus' END) AS sündmus,
    STRING_AGG(DISTINCT CASE 
        WHEN wst.semantic_types NOT IN ('KOHT', 'AEG', 'SEISUND', 'sündmus') 
        THEN wst.semantic_types 
        ELSE NULL 
    END, ', ') AS other_types  -- Collect other semantic types into one column
FROM word_semantic_types wst
GROUP BY wst.word
ORDER BY wst.word;

--QUERY 2: LEIA KÕIK SÕNAD, MILLEL ON 2 SEMANTILIST TÜÜPI
--võta ainult koha, aja, seisundi ja sündmuse sõnad
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
            'koht', 'koht_ala', 'koht_asutus', 'koht_geogr', 'koht_geogr_maailmajagu', 'koht_geogr_veekogu',
            'koht_hoone', 'koht_kehaosa', 'koht_loodus', 'koht_suund/asend', 'abstr_asend/suund', 'ese_anum', 'omadus_koht',
            'aeg', 'aeg_aastaaeg', 'aeg_kuu', 'aeg_nädalapäev', 'aeg_tähtpäev',
            'seisund', 'seisund_haigus', 'seisund_füüs',
            'sündmus'
        )
    )
),
--leia, mis semantiliste tüüpidega iga sõna on + grupeeri koht, aeg, seisund
word_semantic_types as (
SELECT w.value AS word,
            CASE 
                WHEN st.code IN (
                    'koht', 'koht_ala', 'koht_asutus', 'koht_geogr', 'koht_geogr_maailmajagu', 'koht_geogr_veekogu',
                    'koht_hoone', 'koht_kehaosa', 'koht_loodus', 'koht_suund/asend', 'abstr_asend/suund', 'ese_anum', 'omadus_koht') 
                    THEN 'KOHT'
                WHEN st.code IN ('aeg', 'aeg_aastaaeg', 'aeg_kuu', 'aeg_nädalapäev', 'aeg_tähtpäev') 
                    THEN 'AEG'
                WHEN st.code IN ('seisund', 'seisund_haigus', 'seisund_füüs') 
                    THEN 'SEISUND'
                ELSE st.code  -- Keep other types as they are
            END
         AS semantic_types
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
-- Filter only words that have 2 semantic types
SELECT 
    wst.word, wst.semantic_types
FROM word_semantic_types wst
JOIN word_type_counts wtc ON wst.word = wtc.word
WHERE wtc.type_count = 2 -- Only keep words with 2 semantic type
GROUP BY wst.word, wst.semantic_types
ORDER BY wst.word

--QUERY 3: LEIA, MITU SEMANTILIST TÜÜPI IGAL SÕNAL ON
--võta ainult koha, aja, seisundi ja sündmuse sõnad
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
            'koht', 'koht_ala', 'koht_asutus', 'koht_geogr', 'koht_geogr_maailmajagu', 'koht_geogr_veekogu',
            'koht_hoone', 'koht_kehaosa', 'koht_loodus', 'koht_suund/asend',
            'aeg', 'aeg_aastaaeg', 'aeg_kuu', 'aeg_nädalapäev', 'aeg_tähtpäev',
            'seisund', 'seisund_haigus', 'seisund_füüs',
            'sündmus'
        )
    )
),
--leia, mis semantiliste tüüpidega iga sõna on + grupeeri koht, aeg, seisund
word_semantic_types as (
SELECT w.value AS word,
            CASE 
                WHEN st.code IN (
                    'koht', 'koht_ala', 'koht_asutus', 'koht_geogr', 'koht_geogr_maailmajagu', 'koht_geogr_veekogu',
                    'koht_hoone', 'koht_kehaosa', 'koht_loodus', 'koht_suund/asend') 
                    THEN 'KOHT'
                WHEN st.code IN ('aeg', 'aeg_aastaaeg', 'aeg_kuu', 'aeg_nädalapäev', 'aeg_tähtpäev') 
                    THEN 'AEG'
                WHEN st.code IN ('seisund', 'seisund_haigus', 'seisund_füüs') 
                    THEN 'SEISUND'
                ELSE st.code  -- Keep other types as they are
            END
         AS semantic_types
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    JOIN meaning m ON m.id = l.meaning_id 
    JOIN meaning_semantic_type mst ON m.id = mst.meaning_id 
    JOIN semantic_type st ON mst.semantic_type_code = st.code
    WHERE w.value IN (SELECT word FROM words_with_target_types)  -- Limit to words found in Step 1
    GROUP BY w.value, st.code
    )
-- Count distinct semantic types per word
    SELECT word, COUNT(DISTINCT semantic_types) AS type_count
    FROM word_semantic_types
    GROUP BY word;

--QUERY 4: GRUPEERI KOHA/AJA/SÜNDMUSE/SEISUNDI SÕNAD SEMANTILISE TÜÜBI ARVU ALUSEL
--võta ainult koha, aja, seisundi ja sündmuse sõnad
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
            'koht', 'koht_ala', 'koht_asutus', 'koht_geogr', 'koht_geogr_maailmajagu', 'koht_geogr_veekogu',
            'koht_hoone', 'koht_kehaosa', 'koht_loodus', 'koht_suund/asend',
            'aeg', 'aeg_aastaaeg', 'aeg_kuu', 'aeg_nädalapäev', 'aeg_tähtpäev',
            'seisund', 'seisund_haigus', 'seisund_füüs',
            'sündmus'
        )
    )
),
--leia, mis semantiliste tüüpidega iga sõna on + grupeeri koht, aeg, seisund
word_semantic_types as (
SELECT w.value AS word,
            CASE 
                WHEN st.code IN (
                    'koht', 'koht_ala', 'koht_asutus', 'koht_geogr', 'koht_geogr_maailmajagu', 'koht_geogr_veekogu',
                    'koht_hoone', 'koht_kehaosa', 'koht_loodus', 'koht_suund/asend') 
                    THEN 'KOHT'
                WHEN st.code IN ('aeg', 'aeg_aastaaeg', 'aeg_kuu', 'aeg_nädalapäev', 'aeg_tähtpäev') 
                    THEN 'AEG'
                WHEN st.code IN ('seisund', 'seisund_haigus', 'seisund_füüs') 
                    THEN 'SEISUND'
                ELSE st.code  -- Keep other types as they are
            END
         AS semantic_types
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    JOIN meaning m ON m.id = l.meaning_id 
    JOIN meaning_semantic_type mst ON m.id = mst.meaning_id 
    JOIN semantic_type st ON mst.semantic_type_code = st.code
    WHERE w.value IN (SELECT word FROM words_with_target_types)  -- Limit to words found in Step 1
    GROUP BY w.value, st.code
    ),
-- Count distinct semantic types per word
word_type_counts as (
SELECT word, COUNT(DISTINCT semantic_types) AS type_count
    FROM word_semantic_types
    GROUP BY word)
-- Aggregate the results to count how many words have each semantic_type_count
SELECT type_count, COUNT(word) AS word_count
FROM word_type_counts
GROUP BY type_count
ORDER by type_count
;

--QUERY 5: GRUPEERI KOHASÕNAD SEMANTILISE TÜÜBI ARVU ALUSEL
--võta ainult kohasõnad
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
            'koht', 'koht_ala', 'koht_asutus', 'koht_geogr', 'koht_geogr_maailmajagu', 'koht_geogr_veekogu',
            'koht_hoone', 'koht_kehaosa', 'koht_loodus', 'koht_suund/asend'
        )
    )
),
--leia, mis semantiliste tüüpidega iga sõna on + grupeeri koht, aeg, seisund
word_semantic_types as (
SELECT w.value AS word,
            CASE 
                WHEN st.code IN (
                    'koht', 'koht_ala', 'koht_asutus', 'koht_geogr', 'koht_geogr_maailmajagu', 'koht_geogr_veekogu',
                    'koht_hoone', 'koht_kehaosa', 'koht_loodus', 'koht_suund/asend') 
                    THEN 'KOHT'
                WHEN st.code IN ('aeg', 'aeg_aastaaeg', 'aeg_kuu', 'aeg_nädalapäev', 'aeg_tähtpäev') 
                    THEN 'AEG'
                WHEN st.code IN ('seisund', 'seisund_haigus', 'seisund_füüs') 
                    THEN 'SEISUND'
                ELSE st.code  -- Keep other types as they are
            END
         AS semantic_types
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    JOIN meaning m ON m.id = l.meaning_id 
    JOIN meaning_semantic_type mst ON m.id = mst.meaning_id 
    JOIN semantic_type st ON mst.semantic_type_code = st.code
    WHERE w.value IN (SELECT word FROM words_with_target_types)  -- Limit to words found in Step 1
    GROUP BY w.value, st.code
    ),
-- Count distinct semantic types per word
word_type_counts as (
SELECT word, COUNT(DISTINCT semantic_types) AS type_count
    FROM word_semantic_types
    GROUP BY word)
-- Aggregate the results to count how many words have each semantic_type_count
SELECT type_count, COUNT(word) AS word_count
FROM word_type_counts
GROUP BY type_count
ORDER by type_count
;

--QUERY 6: LEIA KÕIK SÕNAD, MILLEL ON AINULT 1 SEMANTILINE TÜÜP JA SEE ON KOHT/AEG/SEISUND/SÜNDMUS
--võta ainult koha, aja, seisundi ja sündmuse sõnad
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
            'koht', 'koht_ala', 'koht_asutus', 'koht_geogr', 'koht_geogr_maailmajagu', 'koht_geogr_veekogu',
            'koht_hoone', 'koht_kehaosa', 'koht_loodus', 'koht_suund/asend', 'abstr_asend/suund', 'ese_anum', 'omadus_koht'
            'aeg', 'aeg_aastaaeg', 'aeg_kuu', 'aeg_nädalapäev', 'aeg_tähtpäev',
            'seisund', 'seisund_haigus', 'seisund_füüs',
            'sündmus'
        )
    )
),
--leia, mis semantiliste tüüpidega iga sõna on + grupeeri koht, aeg, seisund
word_semantic_types as (
SELECT w.value AS word,
            CASE 
                WHEN st.code IN (
                    'koht', 'koht_ala', 'koht_asutus', 'koht_geogr', 'koht_geogr_maailmajagu', 'koht_geogr_veekogu',
                    'koht_hoone', 'koht_kehaosa', 'koht_loodus', 'koht_suund/asend', 'abstr_asend/suund', 'ese_anum', 'omadus_koht') 
                    THEN 'KOHT'
                WHEN st.code IN ('aeg', 'aeg_aastaaeg', 'aeg_kuu', 'aeg_nädalapäev', 'aeg_tähtpäev') 
                    THEN 'AEG'
                WHEN st.code IN ('seisund', 'seisund_haigus', 'seisund_füüs') 
                    THEN 'SEISUND'
                ELSE st.code  -- Keep other types as they are
            END
         AS semantic_types
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
-- Filter only words that have 1 semantic type
SELECT 
    wst.word, wst.semantic_types
FROM word_semantic_types wst
JOIN word_type_counts wtc ON wst.word = wtc.word
WHERE wtc.type_count = 1 -- Only keep words with 1 semantic type
GROUP BY wst.word, wst.semantic_types
ORDER BY wst.word

--QUERY 7: LEIA KÕIK SÕNAD, MILLEL ON AINULT 1 SEMANTILINE TÜÜP JA SEE POLE KOHT/AEG/SEISUND/SÜNDMUS
--võta sõnad, mis pole koha, aja, seisundi ja sündmuse sõnad
WITH words_with_target_types AS (
    SELECT DISTINCT w.value AS word
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    JOIN meaning m ON m.id = l.meaning_id 
    JOIN meaning_semantic_type mst ON m.id = mst.meaning_id 
    JOIN semantic_type st ON mst.semantic_type_code = st.code
    WHERE w.lang = 'est' 
    AND (
        st.code not IN (
            'koht', 'koht_ala', 'koht_asutus', 'koht_geogr', 'koht_geogr_maailmajagu', 'koht_geogr_veekogu',
            'koht_hoone', 'koht_kehaosa', 'koht_loodus', 'koht_suund/asend', 'abstr_asend/suund', 'ese_anum', 'omadus_koht',
            'aeg', 'aeg_aastaaeg', 'aeg_kuu', 'aeg_nädalapäev', 'aeg_tähtpäev',
            'seisund', 'seisund_haigus', 'seisund_füüs',
            'sündmus'
        )
    )
),
--leia, mis semantiliste tüüpidega iga sõna on
word_semantic_types as (
SELECT w.value AS word, st.code
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
    SELECT word, COUNT(DISTINCT code) AS type_count
    FROM word_semantic_types
    GROUP BY word
)
-- Filter only words that have 1 semantic type
SELECT 
    wst.word, wst.code
FROM word_semantic_types wst
JOIN word_type_counts wtc ON wst.word = wtc.word
WHERE wtc.type_count = 1 -- Only keep words with 1 semantic type
GROUP BY wst.word, wst.code
ORDER BY wst.word

--QUERY 8: LEIA KÕIK SÕNAD, MILLEL ON 1 VÕI MITU KOHAGA SOBIVAT MÄRGENDIT
--võta ainult kohasõnad
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
            'koht', 'koht_ala', 'koht_asutus', 'koht_geogr', 'koht_geogr_maailmajagu', 'koht_geogr_veekogu',
            'koht_hoone', 'koht_kehaosa', 'koht_loodus', 'koht_suund/asend', 'abstr_asend/suund', 'ese_anum', 'omadus_koht'
        )
    )
),
--leia, mis semantiliste tüüpidega iga kohasõna on + grupeeri koht ja temaga sobivad märgendid
word_semantic_types as (
SELECT w.value AS word,
            CASE 
                WHEN st.code IN (
                    'koht', 'koht_ala', 'koht_asutus', 'koht_geogr', 'koht_geogr_maailmajagu', 'koht_geogr_veekogu',
                    'koht_hoone', 'koht_kehaosa', 'koht_loodus', 'koht_suund/asend', 'abstr_asend/suund', 'ese_anum', 'omadus_koht') 
                    THEN 'KOHT'
                WHEN st.code IN (
                	'seisund', 'seisund_haigus', 'seisund_füüs', 'sündmus', 'ese_instru', 'ese', 'ese_kunst', 
                	'ese_raha', 'ese_semio', 'ese_riie', 'taim', 'objekt_loodus', 'objekt', 'osa', 'nähtus_loodus') 
                    THEN 'SOBIB'
                ELSE 'OTHER' -- Keep other types as they are
            END
         AS semantic_types
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    JOIN meaning m ON m.id = l.meaning_id 
    JOIN meaning_semantic_type mst ON m.id = mst.meaning_id 
    JOIN semantic_type st ON mst.semantic_type_code = st.code
    WHERE w.value IN (SELECT word FROM words_with_target_types)  -- Limit to words found in Step 1
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

--QUERY 9: LEIA KÕIK SÕNAD, MILLEL ON 1 VÕI MITU AJAGA SOBIVAT MÄRGENDIT
--võta ainult ajasõnad
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
            'aeg', 'aeg_aastaaeg', 'aeg_kuu', 'aeg_nädalapäev', 'aeg_tähtpäev'
        )
    )
),
--leia, mis semantiliste tüüpidega iga kohasõna on + grupeeri koht ja temaga sobivad märgendid
word_semantic_types as (
SELECT w.value AS word,
            CASE 
                WHEN st.code IN (
                    'aeg', 'aeg_aastaaeg', 'aeg_kuu', 'aeg_nädalapäev', 'aeg_tähtpäev') 
                    THEN 'AEG'
                WHEN st.code IN (
                	'esitus', 'nähtus_loodus', 'omadus_aeg') 
                    THEN 'SOBIB'
                ELSE 'OTHER'
            END
         AS semantic_types
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    JOIN meaning m ON m.id = l.meaning_id 
    JOIN meaning_semantic_type mst ON m.id = mst.meaning_id 
    JOIN semantic_type st ON mst.semantic_type_code = st.code
    WHERE w.value IN (SELECT word FROM words_with_target_types)  -- Limit to words found in Step 1
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

--QUERY 10: LEIA KÕIK SÕNAD, MILLEL ON 1 VÕI MITU SEISUNDIGA SOBIVAT MÄRGENDIT
--võta ainult seisundisõnad
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
            'seisund', 'seisund_haigus', 'seisund_füüs'
        )
    )
),
--leia, mis semantiliste tüüpidega iga sõna on + grupeeri seisund ja temaga sobivad märgendid
word_semantic_types as (
SELECT w.value AS word,
            CASE 
                WHEN st.code IN (
                    'seisund', 'seisund_haigus', 'seisund_füüs') 
                    THEN 'SEISUND'
                WHEN st.code IN (
                	'nähtus_psühh', 'nähtus', 'nähtus_loodus', 'omadus_psühh', 'abstr_asend/suund', 'abstr_konkr_omadus', 'ese_raha') 
                    THEN 'SOBIB'
                ELSE 'OTHER'
            END
         AS semantic_types
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    JOIN meaning m ON m.id = l.meaning_id 
    JOIN meaning_semantic_type mst ON m.id = mst.meaning_id 
    JOIN semantic_type st ON mst.semantic_type_code = st.code
    WHERE w.value IN (SELECT word FROM words_with_target_types)  -- Limit to words found in Step 1
    GROUP BY w.value, st.code
    ),
--Put each semantic tag class in a separate column
word_type_counts AS (
    SELECT word, 
           COUNT(DISTINCT semantic_types) AS type_count,
           BOOL_OR(semantic_types = 'SEISUND') AS has_seisund,
           BOOL_OR(semantic_types = 'SOBIB') AS has_sobib,
           BOOL_OR(semantic_types = 'OTHER') AS has_other
    FROM word_semantic_types
    GROUP BY word
)
--vali sellised sõnad, millel on kas 1. üks semantiline tüüp ja see on seisund või 2. kaks semantilist tüüpi ja need on seisund ja sobib
SELECT 
    wtc.word
FROM word_type_counts wtc
WHERE (
    (wtc.type_count = 1 AND wtc.has_seisund)  -- If 1 type, it must be SEISUND
    OR
    (wtc.type_count = 2 AND wtc.has_seisund AND wtc.has_sobib)  -- If 2 types, must be SEISUND and SOBIB
)
ORDER BY wtc.word;

--QUERY 11: LEIA KÕIK SÕNAD, MILLEL ON 1 VÕI MITU SÜNDMUSEGA SOBIVAT MÄRGENDIT
--võta ainult seisundisõnad
WITH words_with_target_types AS (
    SELECT DISTINCT w.value AS word
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    JOIN meaning m ON m.id = l.meaning_id 
    JOIN meaning_semantic_type mst ON m.id = mst.meaning_id 
    JOIN semantic_type st ON mst.semantic_type_code = st.code
    WHERE w.lang = 'est' 
    AND st.code = 'sündmus'
    ),
--leia, mis semantiliste tüüpidega iga sõna on
word_semantic_types as (
SELECT w.value AS word,
            CASE 
	            when st.code = 'sündmus' then 'SÜNDMUS'
                WHEN st.code IN (
                	'tegevus', 'tegevus_tegu', 'ese_kunst', 'abstr/konkr', 'nähtus', 'toit', 
                	'nähtus_füüs', 'tegevus_kõnetegu', 'tegevus_mäng') 
                    THEN 'SOBIB'
                ELSE 'OTHER' -- Keep other types as they are
            END
         AS semantic_types
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    JOIN meaning m ON m.id = l.meaning_id 
    JOIN meaning_semantic_type mst ON m.id = mst.meaning_id 
    JOIN semantic_type st ON mst.semantic_type_code = st.code
    WHERE w.value IN (SELECT word FROM words_with_target_types)  -- Limit to words found in Step 1
    GROUP BY w.value, st.code
    ),
--Put each semantic tag class in a separate column
word_type_counts AS (
    SELECT word, 
           COUNT(DISTINCT semantic_types) AS type_count,
           BOOL_OR(semantic_types = 'SÜNDMUS') AS has_syndmus,
           BOOL_OR(semantic_types = 'SOBIB') AS has_sobib,
           BOOL_OR(semantic_types = 'OTHER') AS has_other
    FROM word_semantic_types
    GROUP BY word
)
--vali sellised sõnad, millel on kas 1. üks semantiline tüüp ja see on sündmus või 2. kaks semantilist tüüpi ja need on sündmus ja sobib
SELECT 
    wtc.word
FROM word_type_counts wtc
WHERE (
    (wtc.type_count = 1 AND wtc.has_syndmus)  -- If 1 type, it must be sündmus
    OR
    (wtc.type_count = 2 AND wtc.has_syndmus AND wtc.has_sobib)  -- If 2 types, must be sundmus and SOBIB
)
ORDER BY wtc.word;

--QUERY 12: LEIA KÕIK SÕNAD, MILLE MÄRGEND EI SAA OLLA KOHT (AGA POLE KA AEG, SÜNDMUS, SEISUND)
--võta ainult mittekohad
WITH words_with_target_types AS (
    SELECT DISTINCT w.value AS word
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    JOIN meaning m ON m.id = l.meaning_id 
    JOIN meaning_semantic_type mst ON m.id = mst.meaning_id 
    JOIN semantic_type st ON mst.semantic_type_code = st.code
    WHERE w.lang = 'est' 
    AND st.code IN (
                	'ese_raha', 'ese_riie', 'esitus_arv', 'esitus_keel', 'esitus_keel_suhtlus', 'esitus_keel_täht', 'esitus_tiitel',
                	'esitus_tähis', 'in_elukutse', 'in_müt', 'in_omadus', 'in_rahvas', 'in_roll', 'in_tegija', 'amet', 'konkr_omadus',
                	'käsklus', 'loom_liik', 'loom_omadus', 'loom_putukas', 'nähtus_psühh', 'omadus', 'omadus_abstr', 'omadus_aeg',
                	'omadus_füüs', 'omadus_kval', 'omadus_psühh', 'tegevus_muutus', 'tegevus_tegu', 'omadus_füüs_värv') 
    ), 
word_semantic_types as (
	SELECT w.value AS word,
            CASE 
                WHEN st.code IN (
                	'ese_raha', 'ese_riie', 'esitus_arv', 'esitus_keel', 'esitus_keel_suhtlus', 'esitus_keel_täht', 'esitus_tiitel',
                	'esitus_tähis', 'in_elukutse', 'in_müt', 'in_omadus', 'in_rahvas', 'in_roll', 'in_tegija', 'amet', 'konkr_omadus',
                	'käsklus', 'loom_liik', 'loom_omadus', 'loom_putukas', 'nähtus_psühh', 'omadus', 'omadus_abstr', 'omadus_aeg',
                	'omadus_füüs', 'omadus_kval', 'omadus_psühh', 'tegevus_muutus', 'tegevus_tegu', 'omadus_füüs_värv') 
                    THEN 'MITTEKOHT'
                ELSE st.code  -- Keep other types as they are
            END
         AS semantic_types
    FROM word w
    JOIN lexeme l ON l.word_id = w.id 
    JOIN meaning m ON m.id = l.meaning_id 
    JOIN meaning_semantic_type mst ON m.id = mst.meaning_id 
    JOIN semantic_type st ON mst.semantic_type_code = st.code
    WHERE w.value IN (SELECT word FROM words_with_target_types)  -- Limit to words found in Step 1
    GROUP BY w.value, st.code
    ),
--Leave no repeat semantic types for the same word
word_type_counts AS (
    -- Count distinct semantic types per word
    SELECT word, COUNT(DISTINCT semantic_types) AS type_count
    FROM word_semantic_types
    GROUP BY word
)
SELECT distinct wst.word
FROM word_semantic_types wst
JOIN word_type_counts wtc ON wst.word = wtc.word
WHERE wtc.type_count = 1 -- Only keep words with 1 semantic type
and wst.semantic_types = 'MITTEKOHT'
GROUP BY wst.word, wst.semantic_types
ORDER BY wst.word

