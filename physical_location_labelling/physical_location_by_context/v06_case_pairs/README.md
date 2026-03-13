Our goal is to filter out errors and semantic anomalies from verb-case patterns (ie - a verb + oblique in illative case is a location 90% of the time, so under what conditions do the other 10% of patterns form so that we could filter them out).



For that we look at pairs of obliques that have the same head verb with different combinations of morphological cases. This will allow us to find coherent patterns of semantic/adverbial types or tagging errors and research what additional conditions are needed for them to form (ie verb type, case order, argumentativeness etc). 



* *casepairs.xslx* - a manually annotated dataset of 980 sentences: 20 sentences per each of the 49 case pairs. The dataset includes a case pair, oblique in the first case, oblique in the second case, their head verb, sentence the obliques and verb appears in, and manual annotation of the obliques' semantics and analysis errors. For a more detailed description see *casepairs\_documentation.md*
* *casepairs\_analysis.md* - manual analysis of the patterns occuring in each case pair. Currently in Estonian
* *casepairs\_documentation.md* - explanations of column names and values in *casepairs.xslx*



