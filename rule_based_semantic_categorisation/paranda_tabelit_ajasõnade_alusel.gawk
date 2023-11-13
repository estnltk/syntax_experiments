#!/usr/bin/gawk
# kasutamine: cat ajasõnad.loend v11_tabel_m1.csv | gawk -F ";" -f  täida_tabelit_ajasõnade_alusel.gawk
# s.t. sisendiks on nii sõnaloend kui märgendatav tabel

# väljad on:
#  1   2      3            4        5        6      7       8      9      10      11       12
# id;verb;verb_compound;obl_root;obl_case;obl_k;ner_loc;ner_per;ner_org;timex;phrase_type;count

# tähtsad käänded:
#   if ($5=="adit" || $5=="ill" || $5=="in" || $5=="el" || 
#       $5=="all" || $5=="ad" || $5=="abl" || $5=="term" || $5=="tr" || $5=="<käändumatu>")  # kohakäändes v. rajav v. saav

BEGIN {ORS=""}

# eeltöö: loe sisse ajasõnade fail

NF==2 {ajas[$1]=$2}   

# päris töö: määra ajamääruseks

NF > 2 && $11!="" {print $0 "\n"}

NF > 2 && $11=="" {    # liik on veel määramata

    tyyp = "";
    # tüüpilisemad ajasõnad
    if ($4 ~ /[^t]öö$/ || $4 ~ /päev$/ || $4 ~ /kuu$/ || $4 ~ /aasta$/ || $4 ~ /aeg$/ || $4 ~ /õhtu$/ || $4 ~ /tund$/)        # liitsõna lõpus on õige sõna
        tyyp = "ajam";
    if ($4 ~ /talv$/ || $4 ~ /suvi$/ || $4 ~ /nädal$/ || $4 ~ /kvartal$/ || $4 ~ /kevad$/ || $4 ~ /hommik$/ || $4 ~ /algus$/ || $4 ~ /sajand$/)        # liitsõna lõpus on õige sõna
        tyyp = "ajam";
    if ($4 ~ /sügis$/ || $4 ~ /kümnend$/ || $4 ~ /dekaad$/ || $4 ~ /moment$/ || $4 ~ /periood$/  || $4 ~ /sekund$/)        # liitsõna lõpus on õige sõna
        tyyp = "ajam";

    if ($5=="adit" || $5=="ill" || $5=="in" || $5=="el")       # sisse, sees või seestütlev
        {
        if (ajas[$4] > 4 && $4 !~ /mine$/)        # ...misse, ...mises ega ...misest pole ajamäärus
            tyyp = "ajam";
        if ($4 == "see" || $4 == "iga" || $4 == "pool" || $4 == "üks")  # pahad sõnad; pole täielik loend muidugi 
            tyyp = "";
        }
    if ($5 == "all")       # alaleütlev
        {
        if (ajas[$4] > 4)
            tyyp = "ajam";
        if ($4 == "see" || $4 == "iga" || $4 == "pool" || $4 == "üks")  # pahad sõnad; pole täielik loend muidugi 
            tyyp = "";
        }
    if ($5 == "ad")       # alalütlev
        {
        if (ajas[$4] > 4)
            tyyp = "ajam";
        if ($4 ~ /mine$/)        # ...misel on ajamäärus
            tyyp = "ajam";
        if ($4 == "see" || $4 == "iga" || $4 == "pool" || $4 == "üks")  # pahad sõnad; pole täielik loend muidugi 
            tyyp = "";
        }
    if ($5 == "abl")       # alaltütlev
        {
        }
    if ($5 == "term")      # rajav
        {
        if (ajas[$4] > 4)
            tyyp = "ajam";
        else if ($4 ~ /mine$/)   # ...miseni on alati ajamäärus
            tyyp = "ajam";
        }
    if ($5 == "tr")       # saav
        {
        if (ajas[$4] > 4 && $4 !~ /mine$/)
            tyyp = "ajam";
        if ($4 == "see" || $4 == "iga" || $4 == "pool" || $4 == "üks")  # pahad sõnad; pole täielik loend muidugi 
            tyyp = "";
        }
    if ($5 == "nom" || $5 == "gen" || $5 == "part" || $5 == "kom" )       # nimetav, omastav, osastav või kaasaütlev
        {
        if (ajas[$4] > 4 && $4 !~ /mine$/)
            tyyp = "ajam";
        if ($4 == "see" || $4 == "iga" || $4 == "pool" || $4 == "üks")  # pahad sõnad; pole täielik loend muidugi 
            tyyp = "";
        if ($4 == "kaks" || $4 == "kolm" || $4 == "neli" || $4 == "viis" || $4 == "kuus" || $4 == "seitse" || $4 == "kaheksa" || $4 == "üheksa" )  # pahad sõnad; pole täielik loend muidugi 
            tyyp = "";
        }
    if ($5 == "part")       # paranda vastu, keset + osastav 
        {
        if ($6=="vastu" || $6=="keset")
            {
            if (tyyp=="")      # polnud ajamäärus, järelikult on kohamäärus
                tyyp="koham";   
            }  
        }
    for (i=1; i<NF-1; i++) 
        print($i ";"); 
    print(tyyp ";" $NF "\n");
}

