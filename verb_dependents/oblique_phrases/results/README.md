## Result files

These files are not manual annotations but results from gpt prompting.

Each subfolder denotes the section and datafile.

 **n20_examples_large_v01**: result files based on data file n20_examples_large_v01.csv.

 **n50_examples_large_v01**: result files based on data file n50_examples_large_v01.csv.

 **n80_examples_large_v01**: result files based on data file n80_examples_large_v01.csv.

 **n80_examples_large_v02**: result files based on data file n80_examples_large_v02.csv.


Each folder is divided into gpt_v0<num> for the step in prompting (v01 is for "physical location prompting", v02 is for abstract location and other prompting). These subfolders do not match the prompt numbers in prompts folder.

In each subfolder the "final result file" is gpt_b10_run01.csv or gpt_10K_b10_run01.csv.

That file has:

| columns | explanation | example |
| sentence_id	| sentence id | 21087297 |
| head_id	| head word id  | 29915194 |
| head_loc	| location of head word in the sentence | 3 |
| verb	| verb |  lootma |
| verb_compound	| verb compound |  |
| morph_case	| case |  in |
| lemma	| lemma of head word |  Marko |
| form	| head word | Markos |
| sentence	| full sentence | moRt: Markos looda saa , kasutab minu arust majapidamisriistana ... |
| timex_tag	| timex tag in the database |  |
| ekilex_tag	| ekilex tag in the database |  |
| ner_tag	| ner tag in the database | LOC |
| classification	| result of prompt: "is it location", answer is yes/no | no |
| explanation	| explanation for the classification | The phrase 'Markos' refers to a person, not a location, so it is not adverbial of place. |
| is_time	| answer to "is it time" prompt, yes/no | no |
| is_alive	| answer to "is it alive" prompt, yes/no | yes |
| is_event	| answer to " is it an event" prompt, yes/no | no |
| is_org	| answer to "is it an organization" prompt, yes/no |  no |
| classification2| for n20 and n50: category (loc, time, event, actor, UNK) |  actor |

For n80_examples_large_v01:
- classification: location prompt, first one and bad results
- classification2: answer to new location prompt, yes/no 
- classification3: category (loc, time, event, actor, UNK)

In case classification=="yes" then the rest of the prompts are not use and therefore those values will be empty.


Additional files waiting manual annotation may be added to subfolders.



 