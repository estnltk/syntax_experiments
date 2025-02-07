# algne fail on v10_koondkorpus_sentences_verb_compound_obl_collocations_20230415-130630.db

#sellest tegin ekspordi DB_Browser for SQLite-i abil (/usr/bin/sqlitebrowser)
# väljade eraldajaks ;

# eemaldasin ühe üleliigse semikooloni:
cat verb_compound_obl_semikoolon.csv | sed 's/size: 12;/size: 12/' \
> verb_compound_obl.csv

# väljad on:
#  1   2      3            4        5        6      7       8      9        10       11    12
# id;verb;verb_compound;obl_root;obl_case;obl_k;ner_loc;ner_per;ner_org;timex;phrase_type;count

# lihtsustan veidi tabelit
cat verb_compound_obl.csv | sed 's/;\-;/;;/g' | sed 's/;\-;/;;/g' | tail +2 \
> v11_tabel.csv

# käändestatistika:
cat v11_tabel.csv | cut -d ';' -f 5 | sort | uniq -c | sort -nr
1005255 gen
 652087 in
 564507 ad
 485806 el
 441723 all
 410447 kom
 218069 part
 159170 nom
 118346 <käändumatu>
 104522 ill
 102605 tr
 101315 adit
  97750 es
  95214 abl
  45727 term
  25941 
  21329 abes

# nii palju on lauseid kokku

cat v11_tabel.csv | gawk -F ";" '{mitu = mitu + $12} END{print(mitu)}'
17516655

# nii palju on lauseid, kus esineb "sõnul"
cat v11_tabel.csv | grep 'sõna;ad;' | gawk -F ";" '{mitu = mitu + $12} END{print(mitu)}'
140835
(samad kahtlased sõnad on veel hinnang, kinnitus, väide, teade, andmed - kõik ad) need katavad vist veel poole sellest hulgast, mida sõnul

# täida tabelit
# 1. etapp: märgi mõned teadaolevad vead ja ner, timex alusel
# ... ja veel obl + kaassõna alusel
cat v11_tabel.csv \
| gawk -F ";" -f märgi_tabelis_vigu.gawk  \
| gawk -F ";" -f täida_tabelit_ner_timex_alusel.gawk \
| gawk -F ";" -f  täida_tabelit_kaassõna_alusel.gawk \
> v11_tabel_m1.csv

# hmm... asesõnad lähevad ka sageli koha-v õi ajamääruseks; selles kohas võib olla vigu, aga ma ei kontrolli neid praegu
# nii palju sai liigitatud:
cat v11_tabel_m1.csv | cut -d ';' -f 11 | grep . | wc -l
1426986
# nii palju jäi liigitamata:
$ cat v11_tabel_m1.csv | cut -d ';' -f 11 | grep -v . | wc -l
3222827

5. mai õhtune seis:
-- täida_tabelit_verbi_alusel.gawk on vist valmis, aga proovimata
kataloogis ~/sveni_projekt/tsepelina/v10
proovisin niimoodi vaadata, millised verbid on mingi kohakäände rektsiooniga:
$ cat tmp2 | grep -v '^[^|]*|[^|]*$' | grep -v '^[^|]*|[^|;]*;0' | grep -v '^[^|]*|.;' | grep 'ill|' | grep -v '|[^|]*|[^|]*ill|' | sed 's/ill|/___ill|___/' | less

nende verbide puhul siis seda kohakäänet ei tohiks lubada...


# idee: võta tabelist ajamääruseks märgendatud read, sealt leiad sõnad, mis on ajamäärusena (aasta, september jms); neid saab kasutada veel märgendamata ridade märgendamiseks

# idee: ajamääruseks sobivad alati sõnad, mis on mitmes eri käändes muudkui ajamääruseks

cat v11_tabel_m1.csv | gawk -F ";" ' $11=="ajam" {a[$4]=0; a[$4 "_" $5]=1;} END{for (b in a) {if (b ~ /_/) {split(b, son, /_/); c[son[1]]=c[son[1]]+1;}} for (b in c) {if (c[b] > 1) print (c[b] " " b);}}' | sort -nr | less

# hmm... siin on 4 korda ka ülikool ja õpetaja; käänded gen, part, el, term kuni
# peaks vist tegema nii, et mõnedes käänetes on rohkem sõnu lubatud kui teistes ? 

# katse: tee fail sõnadest, mis on kindlasti ajasõnad
# failis on sõna;arv
# kus arv tähistab, mitmes käändes esines;
# seda faili võiks käsitsi üksjagu paremaks muuta:
# nt us-lõpulised on paljud selgelt sündmused, mis võiksid olla ajamäärused
# aga sh. on mõned, mis pole;
# on ka üksjagu lihtsõnu, mille olemasolu liitsõna viimase osana tähendab, et sõna liik on teada
# aga praegu selliseid liitsõnu ei püüagi viimase osa alusel liigitada
# lõpp on sageli hoopis "lõpuni" või "lõpuks"; maa on mail, mais, maist jms

cat v11_tabel_m1.csv \
| gawk -F ";" ' $11=="ajam" && $4 !~ /aastane$/ && $4 !~ /ja$/ && $4!="lõpp" && $4!="maa" {a[$4]=0; a[$4 "_" $5]=1;} END{for (b in a) {if (b ~ /_/) {split(b, son, /_/); c[son[1]]=c[son[1]]+1;}} for (b in c) {if (c[b] > 1) print (b ";" c[b]);}}' \
> ajasõnad.loend

cat v11_tabel_m1.csv \
| gawk -F ";" ' $11=="koham" {a[$4]=0; a[$4 "_" $5]=1;} END{for (b in a) {if (b ~ /_/) {split(b, son, /_/); c[son[1]]=c[son[1]]+1;}} for (b in c) {if (c[b] > 1) print (b ";" c[b]);}}' \
> kohasõnad.loend


# täida tabelit
# 2. etapp: märgi ajamäärused ridades, kus varem polnud miskit
#           seejuures kasuta samast tabelist varem tehtud ajasõnade loendit
cat ajasõnad.loend v11_tabel_m1.csv \
| gawk -F ";" -f  täida_tabelit_ajasõnade_alusel.gawk \
> v11_tabel_m2.csv

# tee elusõnade loend keeleveebi korpuse alusel:
./vt_keeleveebi.sh

# täida tabelit
# 3. etapp: märgi tundmatud-määrused ridades, kus varem polnud miskit
#           kasuta seejuures keeleveebi korpusest varem tehtud elusõnade loendit
cat sona_kes_sees.loend v11_tabel_m2.csv \
| gawk -F ";" -f  täida_tabelit_elusate_alusel.gawk \
| gawk -F ";" -f  täida_tabelit_verbi_alusel.gawk \
> v11_tabel_m3.csv

statistika 16. mail:
endiselt liigitamata:
cat v11_tabel_m3.csv | gawk -F ";" '$11=="" {print($11)}' | wc -l
2203508

kuidagi liigitatud:
$ cat v11_tabel_m3.csv | gawk -F ";" '$11!="" {print($11)}' | wc -l
2446305

liigitus täpsemalt:
 cat v11_tabel_m3.csv | gawk -F ";" '$11!="" {print($11)}' | sort | uniq -c
 601981 ajam
1182011 koham
  32368 omajam
  30244 puuviga
 599701 tundmatum

tundmatute käänded:
cat tmptmp.m3 | gawk -F ";" '$11=="" && $5=="all" {print($0)}' | wc -l
281272
cat tmptmp.m3 | gawk -F ";" '$11=="" && $5=="abl" {print($0)}' | wc -l
65079
cat tmptmp.m3 | gawk -F ";" '$11=="" && $5=="ad" {print($0)}' | wc -l
263198
cat tmptmp.m3 | gawk -F ";" '$11=="" && $5=="ill" {print($0)}' | wc -l
0
cat tmptmp.m3 | gawk -F ";" '$11=="" && $5=="in" {print($0)}' | wc -l
0
cat tmptmp.m3 | gawk -F ";" '$11=="" && $5=="el" {print($0)}' | wc -l
353915

kahtlased asjad:
adit on koham, aga tegelt vist väljendi osa
asesõna on koham, aga tegelt vist ikka pole

ja üldse koham on vähem kontrollitud


