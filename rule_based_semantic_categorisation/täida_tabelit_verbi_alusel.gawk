#!/usr/bin/gawk
# kasutamine: | gawk -F ";" -f  täida_tabelit_verbi_alusel.gawk

# mitme käände puhul oleks obl vaikimisi üks asi, v.a mõnede verbide puhul

# väljad on:
#  1   2      3            4        5        6      7       8      9      10      11       12
# id;verb;verb_compound;obl_root;obl_case;obl_k;ner_loc;ner_per;ner_org;timex;phrase_type;count

BEGIN {ORS=""}

$11!="" {print $0 "\n"}

$11=="" {    # liik on veel määramata

    tyyp = "";
    if ($5=="in")       # seesütlev
        {
        if ($2=="avalduma" || $2=="domineerima"  || $2=="kahtlema" || $2=="kahtlustama" || $2=="kajastuma"  || $2=="kehastuma"  || $2=="kehtestuma" )
            tyyp="tundmatum";           # pole aja- ega kohamäärus
        else if ($2=="kihvatama" || $2=="kätkema" || $2=="leppima"  || $2=="lepitama" || $2=="süüdistama")
            tyyp="tundmatum";           # pole aja- ega kohamäärus
        else if (($2=="lööma" && $3=="kaasa"))
            tyyp="tundmatum";           # pole aja- ega kohamäärus
        else
            tyyp="koham";           # julge oletus
            
        }
    if ($5=="ill" || $5=="adit")       # sisseütlev
        {
        if ($2=="armuma" || $2=="haigestuma" || $2=="nakatuma" || $2=="kiinduma"  || $2=="suhtuma" || $2=="uskuma")
            tyyp="tundmatum";           # pole aja- ega kohamäärus   kaasama, kalduma ... ? puutuma
        else if ($2=="riietama" || $2=="rõivastuma" || $2=="rüütama"  || $2=="suikuma" || $2=="sumbuma" || $2=="süvenema"  || $2=="süüvima" || $2=="tuletama" || $2=="turgatama" || $2=="vannutama")
            tyyp="tundmatum";           # pole aja- ega kohamäärus
        else
            tyyp="koham";           # julge oletus
        }

    for (i=1; i<NF-1; i++) 
        print($i ";"); 
    print(tyyp ";" $NF "\n");
}

#el: hoolima, hoiduma, helisema jpm
