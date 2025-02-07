#!/usr/bin/gawk
# kasutamine: | gawk -F ";" -f täida_tabelit_ner_timex_alusel.gawk 

# NB! siin üldse ei arvesta 6. välja ehk kaassõnaga; peaks kontrollima, kas oleks vaja arvestada...

# väljad on:
#  1   2      3            4        5        6      7       8      9      10      11       12
# id;verb;verb_compound;obl_root;obl_case;obl_k;ner_loc;ner_per;ner_org;timex;phrase_type;count

BEGIN {ORS=""}

$11!="" {print $0 "\n"}

$11=="" {    # liik on veel määramata

    tyyp = "";
    if ($7=="" && $8=="" && $9=="")       # igaks juhuks
        {
        if ($10=="match" || $10=="inside")  # on timex --> ajamäärus
            tyyp="ajam";  
        else if ($10=="contains" || $10=="intersects")  # tabeli reas pole infot, et otsustada; peaks alampuud vaatama
            tyyp="";  
        # NB! pole päris kindel, kuidas on liigitatud nt. viieaastasega timex-i mõttes
        }                     
    if ($8=="" && $9=="" && $10=="")       # igaks juhuks
        {
        if ($7=="match" || $7=="inside" || $7=="contains" || $7=="intersects")  # on loc --> kohamäärus
            {
            if ($5=="adit" || $5=="ill" || $5=="in" || $5=="el" || 
                $5=="all" || $5=="ad" || $5=="abl" || $5=="term" || $5=="<käändumatu>")  # kohakäändes v. rajav --> kohamäärus
                tyyp="koham"; 
            else
                tyyp="tundmatum"; 
            if (tyyp=="koham")         # paranda üksikute sõnade kaupa
                {
                if ($4=="aeg" || $4=="päev")
                    tyyp="ajam";
                }
            }
        }                     
    if ($7=="" && $9=="" && $10=="")       # igaks juhuks 
        {
        if ($8=="match" || $8=="inside")  # on per 
            {
            if ($5=="all" || $5=="ad" || $5=="abl")  # väliskohakäändes  --> omajamäärus
                tyyp="omajam";
            else                                     # muidu  --> tundmatu määrus
                tyyp="tundmatum";
            }
        else if ($8=="contains" || $8=="intersects")  # nt Peetri väljak, Peetri aeg  --> per polegi oluline
            ;  
        }
    if ($7=="" && $8=="" && $10=="")      # igaks juhuks
        {
        if ($9=="match" || $9=="inside")  # on org 
            {
            if ($5=="adit" || $5=="ill" || $5=="in" || $5=="el")  # sisekohakäändes  --> kohamäärus
                tyyp="koham";
            if ($5=="all" || $5=="ad" || $5=="abl")  # väliskohakäändes ...
                {
                #ei saa ausaldada if ($4 "maa" || "pea" || "pää" || "mäe")   # ... aga ikka koht  --> kohamäärus
                #tyyp="koham";
                tyyp="omajam";                # väliskohakäändes  --> omajamäärus
                }
            }
        else if ($9=="contains" || $9=="intersects")  #  --> org polegi oluline
            ;  
        }
    for (i=1; i<NF-1; i++) 
        print($i ";"); 
    print(tyyp ";" $NF "\n");
}


