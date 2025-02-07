#!/usr/bin/gawk
# kasutamine: cat sona_kes_sees.loend v11_tabel_m2.csv | gawk -F ";" -f  märgi_verbe_elusate_alusel.gawk
# s.t. sisendiks on nii sõnaloend kui märgendatav tabel

# väljad on:
#  1   2      3            4        5        6      7       8      9      10      11       12
# id;verb;verb_compound;obl_root;obl_case;obl_k;ner_loc;ner_per;ner_org;timex;phrase_type;count

# tähtsad käänded:
#   if ($5=="adit" || $5=="ill" || $5=="in" || $5=="el" || 
#       $5=="all" || $5=="ad" || $5=="abl" || $5=="term" || $5=="tr" || $5=="<käändumatu>")  # kohakäändes v. rajav v. saav

BEGIN {ORS=""}

# eeltöö: loe sisse elusate asjade fail

NF==3 {elus[$1]=$2}   

# päris töö: liigita verbe

NF > 3  {    # liik on veel määramata

    tyyp = "";
    elusus=0;       # vaikimisi on mitte-elus
    if ($4 in elus)           # elus asi või nimi
        elusus=1;
    if ($4 ~ /nna$/ || $4 ~ /lane$/ || $4 ~ /ja$/)    # elus asi või nimi
        elusus=1;
    if ($4 ~ /inimene$/ || $4 ~ /mees$/ || $4 ~ /isik$/ || $4 ~ /naine$/ || $4 ~ /laps$/ || $4 ~ /liige$/ || $4 ~ /poiss$/ )    # elus asi või nimi; liitsõna viimase osa võrdlemine
        elusus=1;

#    for (i=1; i<NF-1; i++) 
#        print($i ";"); 
    print($2 ";" elusus "\n");
}

