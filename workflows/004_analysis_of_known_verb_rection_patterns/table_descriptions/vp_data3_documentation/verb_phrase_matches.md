# Description of verb_phrase_matches table

The table contains information about patterns and their matches in transactions database (v32). Each row contains pattern ID in table *patterns*, transaction head ID in transactions database of a transaction containing a match to given pattern and phrase number from table *patterns*.

| Column name | Description | Example
|---|---|---|
|pat_id| Pattern ID in table *patterns* | 1252
|head_id| Head ID of a transaction containing a match to given pattern | 66
|phrase_nr| Phrase number in table *patterns* (1 or 2) | 1


## Additional information

-