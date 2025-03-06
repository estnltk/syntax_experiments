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
--JA VÄHEMALT 1 KOHA/AJA/SEISUNDI/SÜNDMUSE TÄHENDUS JA SÕNA KÕIK SEMANTILISED TÜÜBID
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
word_type_counts AS (
    -- Count distinct semantic types per word
    SELECT word, COUNT(DISTINCT semantic_types) AS type_count
    FROM word_semantic_types
    GROUP BY word
)
-- Filter only words that have more than 1 semantic type
SELECT 
    wst.word,
    MAX(CASE WHEN wst.semantic_types = 'KOHT' THEN '✓' END) AS koht,
    MAX(CASE WHEN wst.semantic_types = 'AEG' THEN '✓' END) AS aeg,
    MAX(CASE WHEN wst.semantic_types = 'SEISUND' THEN '✓' END) AS seisund,
    MAX(CASE WHEN wst.semantic_types = 'sündmus' THEN '✓' END) AS sündmus,
    STRING_AGG(DISTINCT CASE 
        WHEN wst.semantic_types NOT IN ('KOHT', 'AEG', 'SEISUND', 'sündmus') 
        THEN wst.semantic_types 
        ELSE NULL 
    END, ', ') AS other_types
FROM word_semantic_types wst
JOIN word_type_counts wtc ON wst.word = wtc.word
WHERE wtc.type_count = 2 -- Only keep words with 2 semantic types
GROUP BY wst.word
ORDER BY wst.word

--QUERY 3: LEIA KÕIK SÕNAD, MILLEL ON AINULT 1 SEMANTILINE TÜÜP JA SEE ON KOHT/AEG/SEISUND/SÜNDMUS
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
word_type_counts AS (
    -- Count distinct semantic types per word
    SELECT word, COUNT(DISTINCT semantic_types) AS type_count
    FROM word_semantic_types
    GROUP BY word
)
-- Filter only words that have more than 1 semantic type
SELECT 
    wst.word, wst.semantic_types
FROM word_semantic_types wst
JOIN word_type_counts wtc ON wst.word = wtc.word
WHERE wtc.type_count = 1 -- Only keep words with 1 semantic type
GROUP BY wst.word, wst.semantic_types
ORDER BY wst.word

--QUERY 4: LEIA, MITU SEMANTILIST TÜÜPI IGAL SÕNAL ON
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

--QUERY 5: GRUPEERI SÕNAD SEMANTILISE TÜÜBI ARVU ALUSEL
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

--QUERY 6: GRUPEERI KOHASÕNAD SEMANTILISE TÜÜBI ARVU ALUSEL
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

--QUERY 7: LEIA KÕIK VERBID, MILLEL ON AINULT 1 SEMANTILINE TÜÜP
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
word_type_counts AS (
    -- Count distinct semantic types per word
    SELECT word, COUNT(DISTINCT semantic_types) AS type_count
    FROM word_semantic_types
    GROUP BY word
)
-- Filter only words that have more than 1 semantic type
SELECT 
    wst.word, wst.semantic_types
FROM word_semantic_types wst
JOIN word_type_counts wtc ON wst.word = wtc.word
WHERE wtc.type_count = 1 -- Only keep words with 1 semantic type
GROUP BY wst.word, wst.semantic_types
ORDER BY wst.word

--QUERY 8: LEIA KÕIK SÕNAD, MILLEL ON AINULT 1 SEMANTILINE TÜÜP JA SEE POLE KOHT/AEG/SEISUND/SÜNDMUS
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
            'koht_hoone', 'koht_kehaosa', 'koht_loodus', 'koht_suund/asend',
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