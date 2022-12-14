- *sketch_data_prep.ipynb* - nb eksperimentide test ja treeningsetide koostamiseks ()
- *sketches.py* - sketchide koostamine
Sketchide põhimõte: 
For grouping, we use abstractions of a syntax tree.
Such syntax-sketches can be defined in various ways.
Let d(x) and p(x) denote the dependency and part-of-speech labels for a node *x* and let *c(x)* denote the size of the subtree.
Then  we can define syntax sketches for clauses as
*p(r){d(x1)c(x1),..., d(xn)c(xn)}*
where *r* is the root of the clause with child nodes *x1,..., xn*.
For *c(x)* three sizes -- short, long, extra long -- are distinguished.
Short being subtree of only up to two nodes (including child node itself), long consisting of up to nine nodes and extra long being ten or more nodes. 
Top 50 most frequent sketches featured no sketches with extra long subtrees. Possible roots are grouped into three by partofspeech-tags: first group for verbs, second for most-common non-verbal roots (e.g substantives and adjectives) and third for the rest.


###Experiment 2
- *splits* - dev ja train setid, kust igast on välja visatud vastav sketch
    - *test_50* - test setid, millest iga sisaldab lauseid, mida iseloomustab üks 50 sagedasemast sketchist
- *outputs* - mudelid, kust välja visatud valitud sketchid (sketch failinimes); parsitud test-setid igale mudelile
- *random_splits2* - sama, mis *splits*, aga iga sketchi asemel on välja visatud
suvalised osalaused vastavalt sketchi esinemissagedusele

---
- *no_sketch_splits* - kõik sketchid treeningust välja visatud
    * dev.conllu ja train.conllu - sketchid välja visatud
    * dev_random.conllu ja train_random.conllu - juhuslikud osalaused välja visatud sketchidega võrdväärses koguses
- *no_sketch_outputs* - mudelid ja parsitud testid kõigil sketchidel

---
- *03_prediction.py* - testide parsimiseks
- *04_evaluation.py* - parsitud testide hindamiseks (LAS) ja tulemuste csv-sse kirjutamiseks

