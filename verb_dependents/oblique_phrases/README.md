## Problem statement

Many combinations of verbs-case forms clearly determine the semantic role of the word that appears in a given position in a sentence:

- whether it is an adverbial of place 
- adverb of time
- an event
- an agent/actor (a participant referring to a person/organization)
- adverbial of manner 
- cause/condition
- construction
- or an element that belongs to the verb’s argument structure

Our aim is to study this phenomenon through statistical analysis of large-scale sentence annotations.

To do this, we use EKILEX dictionaries and LLMs to assign semantic categories, along with simple statistical methods to group the results, and manual annotation to identify interesting linguistic hypotheses.


## Workflow

- Use existing labels to filter data 
- Group data 
- Use GPT to relabel data 
- Final analysis



## Files

[data](data) -- input files for gpt prompting

[locative_adverbial](locative_adverbial) -- benchmarks and code for prompting

[results](results) -- result files from gpt prompting

[summary](summary) -- summary file that shows the work progress

[workflow](workflow) -- [v04](https://github.com/estnltk/syntax_experiments/tree/semantic_labelling/physical_location_labelling/physical_location_by_context/v04_verb-case_pattern/code) workflow to include timex and ner tags in tables

NB!  The gpt code expects python >=3.10

