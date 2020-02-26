# Syntax Experiments 

add_input_layers.py adds experiment layers to all of the text objects in both collections in database. All experiments are
done with gold_syntax and automorph syntax. Automorph experiment layers use morphological features automatically tagged with
VISL tagger. 

Experiments' descriptions in Estonian: 

Experiment 1: kõik lemmad alles <br>
Experiment 2: kõik lemmad kustutatud <br>
Experiment 3: nimisõnade ja omadussõnade lemmad kustutatud <br>
Experiment 3_2: kõik sõnavormid kustutatud + nimisõnade ja omadussõnade lemmad kustutatud  <br>
Experiment 4: verbide ja kaassõnade lemmad kustutatud <br>
Experiment 4_2: kõik sõnavormid kustutatud + verbide ja kaassõnade lemmad kustutatud <br>
Experiment 5: kõik sõnavormid kustutatud + kustutatud kõik lemmad, mis ei esine CG reeglites <br>
Experiment 6: kõik käänded kustutatud <br>
Experiment 6_2: kõik käänded ja sõnavormid kustutatud <br>
Experiment 7: osad käänded kustutatud (nom, gen, part, adit) <br>
Experiment 7_2: osad käänded kustutatud (nom, gen, part, adit) + sõnavormid <br>
Experiment 8: teised osad käänded kustutatud (kõik peale nom, gen, part, adit) <br>
Experiment 8_2: teised osad käänded kustutatud (kõik peale nom, gen, part, adit) + sõnavormid <br>
Experiment 9: alles ainult postagid jm sünt märgendid <br>
Experiment 10: alles ainult tekstisõnad (ja sünt märgendus) <br>
Experiment 11: kustutatud tekstisõnad, alles kõik muu <br>
Experiment 12: kustutatud tekstisõnad ja lemmad <br>
Experiment 13: kustutatud tekstisõnad ja juhuslikult 19,5% lemmadest <br>
Experiment 14: kustutatud tekstisõnad ja juhuslikult 42,3% lemmadest <br>

<br>

Now every text object in the collections have these layers:
1) words <br>
2) compound_tokens <br>
3) sentences <br>
4) syntax_gold <br>
5) gm_experiment_1 <br>
6) gm_experiment_2 <br>
7) gm_experiment_3 <br>
8) gm_experiment_3_2 <br>
9) gm_experiment_4 <br>
10) gm_experiment_4_2 <br>
11) gm_experiment_5 <br>
12) gm_experiment_6 <br>
13) gm_experiment_6_2 <br>
14) gm_experiment_7 <br>
15) gm_experiment_7_2 <br>
16) gm_experiment_8 <br>
17) gm_experiment_8_2 <br>
18) gm_experiment_9 <br>
19) gm_experiment_9 <br>
20) gm_experiment_10 <br>
21) gm_experiment_11 <br>
22) gm_experiment_12 <br>
23) gm_experiment_13 <br>
24) gm_experiment_14 <br>
25) am_experiment_1 <br>
26) am_experiment_2 <br>
27) am_experiment_3 <br>
28) am_experiment_3_2 <br>
29) am_experiment_4 <br>
30) am_experiment_4_2 <br>
31) am_experiment_5 <br>
32) am_experiment_6 <br>
33) am_experiment_6_2 <br>
34) am_experiment_7 <br>
35) am_experiment_7_2 <br>
36) am_experiment_8 <br>
37) am_experiment_8_2 <br>
38) am_experiment_9 <br>
39) am_experiment_9 <br>
40) am_experiment_10 <br>
41) am_experiment_11 <br>
42) am_experiment_12 <br>
43) am_experiment_13 <br>
44) am_experiment_14 <br>
