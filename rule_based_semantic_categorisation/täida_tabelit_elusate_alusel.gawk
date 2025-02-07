#!/usr/bin/gawk
# kasutamine: cat sona_kes_sees.loend v11_tabel_m2.csv | gawk -F ";" -f  täida_tabelit_elusate_alusel.gawk
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

# päris töö: määra omajamääruseks ja/või kohamääruseks

NF > 3 && $11!="" {print $0 "\n"}

NF > 3 && $11=="" {    # liik on veel määramata

    tyyp = "";
    elusus=0;       # vaikimisi on mitte-elus
    if ($4 in elus)           # elus asi või nimi
        elusus=1;
    if ($4 ~ /nna$/ || $4 ~ /lane$/ || $4 ~ /ja$/)    # elus asi või nimi
        elusus=1;
    if ($4 ~ /inimene$/ || $4 ~ /mees$/ || $4 ~ /isik$/ || $4 ~ /naine$/ || $4 ~ /laps$/ || $4 ~ /liige$/ || $4 ~ /poiss$/ )    # elus asi või nimi; liitsõna viimase osa võrdlemine
        elusus=1;
    if ($4 ~ /tänav$/ || $4 ~ /aadress$/ || $4 ~ /maja$/)       # elusate asjade failis on vigu...
        elusus=0;

    if ($5=="gen" || $5=="<käändumatu>")       # omastav või <käändumatu>   vaikimisi võiks olla mitte-määrus
        {
        if ($6=="järel")
            {
            if (elusus==1 || $4 ~ /^[:upper:]/)    # elus asi või nimi, viimane on sage spordis (Jussi järel)
                ;
            else                                   
                tyyp = "ajam";
            }
        }                    
    if ($5=="adit" || $5=="ill" || $5=="in" || $5=="el")       # sisse, sees või seestütlev
        {
        if (elusus==1)        
            tyyp = "tundmatum";
        }
    if ($5=="all" || $5=="ad" || $5=="abl")       # alale, alal või alaltütlev
        {
        if (elusus==1 && $4 !~ /mine$/)
            tyyp = "tundmatum";
        }
    if ($5 == "term" || $5 == "tr")      # rajav
        {
        if (elusus==1)
            tyyp = "tundmatum";
        }
    for (i=1; i<NF-1; i++) 
        print($i ";"); 
    print(tyyp ";" $NF "\n");
}

