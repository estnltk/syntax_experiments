# Syntax experiments

Various experiments with syntax analysers splitted among different branches.

### I. Ablation experiments

Investigations on the impact of training set size, morphological features and clausal patterns on syntactic parsing; experiments with parsing model ensembles; automatic evaluation and investigation of parsing errors

**Branch:** [ablation_experiments](https://github.com/estnltk/syntax_experiments/tree/ablation_experiments) 


### II. Syntax consistency

Search for sentence level modifications that preserve syntax. In theory, syntax should be conserved when free entities are removed from sentences. Sometimes this is also true for bound entities such as objects. In practice, additional factors, such as interpunctuation and wording consistency, have a big inpact on the outcomes.

The branch contains workflows for shortening sentences and preparing the results for manual labelling followed by small analysis of the results. Experiments are done for different phrase types where each phrase type is defined by the dependency relation predicted by stanza syntax analyser.  

**Branch:** [syntax_consistency](https://github.com/estnltk/syntax_experiments/tree/syntax_consistency) 


### III. Consistency between adverbial phrases and named entities 

Adverbial phrases often coincide with geographical location or time expression, but not always. In these experiments, we study this problem in detail. For that we use a stanza syntax analyzer to extract adverbials and dedicated taggers for isolating named entities and time expressions. After that we build a workflow for extracting sentences where these annaotations are in potential conflict and extract corresponding sentences for manual labelling.  
 
**Branch:**  [adverbials](https://github.com/estnltk/syntax_experiments/tree/adverbials) 

### IV. Other brances

* [semantic_labelling](https://github.com/estnltk/syntax_experiments/tree/semantic_labelling) -- <i>(add description here)</i>
* [subcat](https://github.com/estnltk/syntax_experiments/tree/subcat) -- <i>(add description here)</i> 
* [legacy](https://github.com/estnltk/syntax_experiments/tree/legacy) -- legacy experiments and developments, no longer supported;