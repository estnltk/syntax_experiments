## Problem statement

Paljud verb-käändepaari kombinatsioonid määravad üheselt ära vastavasse lünka mineva sõna semantilise rolli:

- kas see on aja või kohamäärus

- viisimäärus

- või on see verbi argumendistruktuuri kuuluv element

Meie eesmärk on uuroda antud probleemi lausete massmärgenduste statistilse analüüsiga. 

Selleks kasutame EKILEX-i sõnastikke ja LLM-e sementiliste kategooriate märgendamiseks ning lihtsat statistilist analüüsi tulemususte grupeerimiseks ning käsitsi märgendamist huvitavate lingvistiliste hüpoteeside tuvastamiseks.




## Files

[data](data) -- input files for gpt prompting

[locative_adverbial](locative_adverbial) -- benchmarks and code for prompting

[results](results) -- result files from gpt prompting

[summary](summary) -- summary file that shows the work progress

[workflow](workflow) -- [v04](https://github.com/estnltk/syntax_experiments/tree/semantic_labelling/physical_location_labelling/physical_location_by_context/v04_verb-case_pattern/code) workflow to include timex and ner tags in tables

NB!  The gpt code expects python >=3.10

