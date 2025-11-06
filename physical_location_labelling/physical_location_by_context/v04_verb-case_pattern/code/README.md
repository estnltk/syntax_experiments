## Code files for different development tasks

### Workflow:
1. Create a conda environment with the needed packages: ***environment_v04.yml***
2. Make wordlists for different semantic types:
    - ***adverbs_ekilex_script.sql***: Sql queries for extracting adverb wordlists from ekilex.
    - ***oblique_ekilex_script.sql***: Sql queries for extracting oblique wordlists from ekilex.
3. Find all adverbials (adverbs and obliques in spatial cases) from the Estonian Reference corpus and write them into a separate database table: ***v04_adverbials_from_SQLite.ipynb*** 
4. Annotate adverbials in that table by using the wordlists created in the previous step: ***v04_semtype_to_database.ipynb*** 
5. Calculate semantic tag coverage and lemma frequency for adverbials in the aformentioned database tables: ***v04_statistics_lemma.ipynb***
6. Find semantic type statistics of verb-case patterns and verbs
    - Calculate tag frequency, binary logarithm and amount of unique dependents per verb for adverbs: ***v04_statistics_verb_adverb.ipynb*** 
    - Seperate case from feats. Find verb-case patterns. Calculate tag frequency, binary logarithm and amount of unique dependents per verb-case pattern: ***v04_statistics_verb_case.ipynb***
7. Count the amount of synsets each verb has in Estonian Wordnet. Add it to database table. Used for data visualization.: ***v04_synsets_wordnet.ipynb***
8. Create various hoverplots to illustrate whether verb-case patterns prefer obliques of a specific semantic type **or** verbs prefer adverbs of a specific semantic type : ***v04_visualization.ipynb***
