#!/usr/bin/gawk
# kasutamine: | gawk -F ";" -f märgi_tabelis_vigu.gawk 

# väljad on:
#  1   2      3            4        5        6      7       8      9      10      11       12
# id;verb;verb_compound;obl_root;obl_case;obl_k;ner_loc;ner_per;ner_org;timex;phrase_type;count

BEGIN {ORS=""}

$11!="" {print $0 "\n"}

$11=="" {    # liik on veel määramata

    tyyp = "";
    if ($5=="ad" || $5=="all") 
        { 
    	if ($4=="sõna" || $4=="hinnang" || $4=="kinnitus" || $4=="väide" || $4=="teade" || $4=="andmed")
            tyyp="puuviga";
        }
    if ($5=="in") 
        { 
    	if ($4=="suhe" || $4=="kord" || $4=="koha" || $4=="käsi")
            tyyp="puuviga";
        }
    for (i=1; i<NF-1; i++) 
        print($i ";"); 
    print(tyyp ";" $NF "\n");
}

