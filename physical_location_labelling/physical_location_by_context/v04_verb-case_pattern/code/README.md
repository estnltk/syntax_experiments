## Code files for different development tasks

**v04_rulebased_annotation**: Annotating adverbials with semantic types through wordlists. Finding and researching verb-case patterns. Seeing whether verbs prefer a specific type of adverb.

Workflow:
1. *environment_v04.yml*: creating a conda environment with the needed packages
2. Making wordlists by semantic type:
    1.1. *adverbs_ekilex_script.sql*: Sql queries for extracting adverb wordlists from ekilex.
    1.2. *oblique_ekilex_script.sql*: Sql queries for extracting oblique wordlists from ekilex.
3. *v04_adverbials_from_SQLite.ipynb*: Finds all adverbials (adverbs and obliques in spatial cases) from the Estonian Reference corpus and writes them into a separate database table
4. *v04_semtype_to_database.ipynb*: Adds semantic tags from wordlist to adverbials in the tables created in the previous step
5. *v04_statistics_lemma.ipynb*: Calculates semantic tag coverage and lemma frequency for adverbials in the aformentioned database tables
6. Find semantic type statistics of verb-case patterns and verbs
    5.1. *v04_statistics_verb_case.ipynb*: Seperates case from feats. Finds verb-case patterns. Calculates tag frequency, binary logarithm and amount of unique dependents per verb-case pattern
    5.2. *v04_statistics_verb_adverb.ipynb* Calculates tag frequency, binary logarithm and amount of unique dependents per verb for adverbs
7. *v04_synsets_wordnet.ipynb*: counts the amount of synsets each verb has in Estonian Wordnet. Adds it to database table. Used for data visualization.
8. *v04_visualization.ipynb*: creates various hoverplots to illustrate whether
    * verb-case patterns prefer obliques of a specific semantic type
    * verbs prefer adverbs of a specific semantic type 
