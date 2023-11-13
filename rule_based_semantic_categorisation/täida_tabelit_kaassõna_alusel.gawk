#!/usr/bin/gawk
# kasutamine: | gawk -F ";" -f  täida_tabelit_kaassõna_alusel.gawk

# väljad on:
#  1   2      3            4        5        6      7       8      9      10      11       12
# id;verb;verb_compound;obl_root;obl_case;obl_k;ner_loc;ner_per;ner_org;timex;phrase_type;count

BEGIN {ORS=""}

$11!="" {print $0 "\n"}

$11=="" {    # liik on veel määramata

    tyyp = "";
    if ($5=="all")       # alaleütlev
        {
        if ($6=="tänu" || $6=="vaatamata" || $6=="vastavalt")
            tyyp="tundmatum";           # pole aja- ega kohamäärus
        }
    if ($5=="el")       # seestütlev  vaikimisi võiks olla kohamäärus???
        {
        if ($6=="hoolimata")
            tyyp="tundmatum";           # pole aja- ega kohamäärus
        if ($6=="alates" || $6=="saati" || $6=="saadik" || $6=="peale")
            tyyp="ajam"; 
        }
    if ($5=="gen" || $5=="<käändumatu>")       # omastav või <käändumatu>   vaikimisi võiks olla mitte-määrus
        {
        if ($6=="aegu" || $6=="ajal" || $6=="algul" || $6=="eel" || $6=="hakul" || $6=="jooksul" || $6=="kestel" || $6=="käigus" || $6=="paiku")
            tyyp="ajam";   
        if ($6=="vältel")
            tyyp="ajam";   
        
        # NB! siin on arvestamata, et gen sõna ise võiks oma tähendusega liigi ära muuta, nt. "aasta sees" pole kohamäärus           
        if ($6=="alla" || $6=="kandis" || $6=="keskel" || $6=="lähedale" || $6=="peal" || $6=="pool" || $6=="sees" || $6=="tagant" || $6=="taha")
            tyyp="koham";    # NB! see võib olla ka ajamäärus!!!       
        if ($6=="all" || $6=="alt" || $6=="ees" || $6=="ette" || $6=="hulgas" || $6=="hulgast" || $6=="hulka")
            tyyp="koham";           
        if ($6=="juurde" || $6=="juures" || $6=="juurest" || $6=="kannul" || $6=="kannule" || $6=="kannult")
            tyyp="koham";   
        if ($6=="kaugusel" || $6=="keskele" || $6=="keskelt" || $6=="kohal" || $6=="kohale" || $6=="kohalt" || $6=="kõrval" || $6=="kõrvale" || $6=="kõrvalt" )
            tyyp="koham";   
        if ($6=="külge" || $6=="küljes" || $6=="küljest" || $6=="küüsi" || $6=="küüsis" || $6=="küüsist" || $6=="ligidal" || $6=="ligidale" || $6=="ligidalt" )
            tyyp="koham";   
        if ($6=="lähedal" || $6=="lähedalt" || $6=="lähistel" || $6=="man" || $6=="mant" || $6=="manu" || $6=="najale" || $6=="najalt")
            tyyp="koham";   
        if ($6=="nõjal" || $6=="otsas" || $6=="otsast" || $6=="seest" || $6=="sisse" || $6=="suunas" || $6=="taga")
            tyyp="koham";   
        if ( $6=="vahele" || $6=="vahelt" || $6=="varjus" || $6=="vastas" || $6=="vastast" || $6=="vastu")
            tyyp="koham";
        if ($6=="veerde" || $6=="veeres" || $6=="veerest" || $6=="õlule" || $6=="äärde" || $6=="ääres" || $6=="äärest" || $6=="ümbert")
            tyyp="koham";   
                    
        if ($6=="abil" || $6=="ajel" || $6=="arust" || $6=="arvel" || $6=="arvele" || $6=="arvelt" || $6=="asemel" || $6=="asemele")
            tyyp="tundmatum";           # pole aja- ega kohamäärus
        if ($6=="heaks" || $6=="jaoks" ||  $6=="jõul" || $6=="järgi" || $6=="kallal" || $6=="kallale" || $6=="kallalt")
            tyyp="tundmatum";           # pole aja- ega kohamäärus
        if ( $6=="kilda" || $6=="kiuste" || $6=="kohaselt" || $6=="kohta" || $6=="kombel" || $6=="korral" || $6=="kujul" )
            tyyp="tundmatum";           # pole aja- ega kohamäärus
        if ($6=="kulul" || $6=="meelest" || $6=="moel" || $6=="moodi" || $6=="mõjul" || $6=="näol" || $6=="osas" || $6=="pihta" || $6=="poolest")
            tyyp="tundmatum";           # pole aja- ega kohamäärus
        if ($6=="puhul" || $6=="põhjal" || $6=="päralt" || $6=="raames" || $6=="saatel" || $6=="seas")
            tyyp="tundmatum";           # pole aja- ega kohamäärus
        if ($6=="seast" || $6=="suhtes" || $6=="sunnil" || $6=="takka" || $6=="tarvis" || $6=="teel" || $6=="toel" || $6=="tõttu" || $6=="tõukel")
            tyyp="tundmatum";           # pole aja- ega kohamäärus
        if ($6=="viisi" || $6=="väel" || $6=="väele")
            tyyp="tundmatum";           # pole aja- ega kohamäärus
            
        if ($6=="eest" || $6=="järel" || $6=="kanti" || $6=="ligi" || $6=="ümber")
            tyyp="";                    # võib olla ajamäärus ; üks hilisem skript peaks ajasõnade põhjal otsustama   
        if ($6=="pärast" || $6=="ringi" || $6=="ringis" || $6=="haaval" || $6=="kaupa" || $6=="piires" || $6=="võrra" || $6=="üle")
            tyyp="";                    # võib olla ajamäärus ; üks hilisem skript peaks ajasõnade põhjal otsustama
        if ($6=="järele" || $6=="järelt")
            tyyp="";                    # ei oska praegu midagi otsustada; vaja vist vaadata ka sõna ennast ja/või verbi    
        if ($6=="kaudu" || $6=="käes" || $6=="käest" || $6=="kätte" || $6=="läbi" || $6=="najal" || $6=="otsa" || $6=="peale" || $6=="pealt" )
            tyyp="";                    # ei oska praegu midagi otsustada; vaja vist vaadata ka sõna ennast ja/või verbi       
        if ($6=="poole" || $6=="poolt" || $6=="vahel")
            tyyp="";                    # ei oska praegu midagi otsustada; vaja vist vaadata ka sõna ennast ja/või verbi
        }
    if ($5=="part")       # osastav
        {
        if ($6=="enne" || $6=="peale" || $6=="pärast")
            tyyp="ajam";   
        if ($6=="kaudu" ||  $6=="mööda" || $6=="teispool" || $6=="väljapoole" || $6=="väljaspool" || $6=="väljastpoolt")
            tyyp="koham";   
        }
    if ($5=="term")       # rajav
        {
        if ($6=="kuni")
            tyyp="";       # neid pole timex juba märgendanud... tegelt on siin lihtsalt sageli mingid ajasõnad nagu detsember; + mine-tuletised jms     
        }

    if (tyyp=="ajam")      # paljudel juhtudel ajamäärus ei saa olla võimalik sõna tähenduse tõttu NB!! need loendid on POOLIKUD !!!
        {
        if ($4 ~ /aastane$/)        # 5aastane jms
            tyyp="";
        if ($4 ~ /[:digit:]%$/ || $4 ~ /[:digit:].?g$/ || $4 ~ /Hz$/ || $4 ~ /[:digit:].?m$/)        # 5% 5kg jms, s.t. arv+ühik 
            tyyp="";
        if ($4 ~ /kroon$/ || $4 ~ /meeter$/ || $4 ~ /gramm$/ || $4 ~ /[hH]erts$/ || $4 ~ /protsent$/)        # kuni ... kroonini, grammini, meetrini, hertsini jm ühikud
            tyyp="";
        if ($4 ~ /ala$/ || $4 ~ /tonn$/ || $4 ~ /kraad$/)        # kuni ... ühikud? jms
            tyyp="";
        if ($4 ~ /tänav$/ || $4 ~ /meri$/ || $4 ~ /sadam$/ || $4 ~ /korrus$/ || $4 ~ /ristmik$/  || $4 ~ /tee$/)        # kuni ... koht
            tyyp="";
        if ($4 ~ /silmapiir$/ || $4 ~ /maja$/ || $4 ~ /sild$/ || $4 ~ /rand$/)        # kuni ... koht
            tyyp="";
        if ($4 ~ /pikkus$/ || $4 ~ /laius$/ || $4 ~ /kõrgus$/ || $4 ~ /kaal$/ || $4 ~ /paksus$/ || $4 ~ /tase$/ || $4 ~ /punkt$/ || $4 ~ /piir$/)        # hmm... mõõtmed
            tyyp="";
        if ($4 ~ /kael$/)        # hmm... kehaosad
            tyyp="";
        }
    if (tyyp=="koham")      # paljudel juhtudel kohamäärus ei saa olla võimalik sõna tähenduse tõttu NB!! need loendid on POOLIKUD !!!
        {
        # mõned erandlikud väljendid
        if ($4=="muu" && $5=="gen" && $6=="hulgas")        
            tyyp="";
        if ($4=="nimi" && $5=="gen" && $6=="all")        
            tyyp="";
        if ($4=="silm" && $5=="gen" && $6=="all")        
            tyyp="";
        }
    for (i=1; i<NF-1; i++) 
        print($i ";"); 
    print(tyyp ";" $NF "\n");
}


