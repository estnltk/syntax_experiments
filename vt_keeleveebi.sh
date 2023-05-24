#!/bin/sh

# väljad
#     1          2                 3              4          5          6            7            8
# lause nr \t sõna nr lauses \t osalause nr \t sõnavorm \t lemma \t morfi lemma \t sõnaliik \t gram kat-d
#tee elusolendite loend: sõna, millele järgneb ", kes"

# tõsta tasakaalus korpuse osa ajutiselt kõrvale, et see statistikat ei segaks
mv ~/svnkrpkirjak/keeleveeb/balanced.data.idx ~/svnkrpkirjak/keeleveeb/balanced.data.idx2

# sõnad, mis on konstruktsiooni ", kes" ees
# ... tähistavad vist elus asju?
cat ~/svnkrpkirjak/keeleveeb/*.data.idx \
| gawk '{a1=a2; a1pos=a2pos; a2=kes; a2pos=kepos; ke=$4; kes=$5; kepos=$7; if (kes=="kes") {if (a2=="," && a1pos=="S") print(a1)}}' \
| sort | uniq -c | sort -nr \
> elusolendid.srt

# sõnad, mis on seesütlevas käändes
cat ~/svnkrpkirjak/keeleveeb/*.data.idx \
| tr ';\t' '_;' \
| gawk -F ";" '$8 ~ /Ine/ {print($5)}' \
| sort | uniq -c | sort -nr \
> seesütlevas.srt


# tõsta tasakaalus korpuse kõrvaletõstetud osa tagasi
mv ~/svnkrpkirjak/keeleveeb/balanced.data.idx2 ~/svnkrpkirjak/keeleveeb/balanced.data.idx

# sordi sõnade järgi
cat elusolendid.srt | LC_COLLATE=C sort -k 2  > elusolendid.srt2
cat seesütlevas.srt | LC_COLLATE=C sort -k 2  > seesütlevas.srt2


# pane kokku ja võta need, mis on pigem elus
# tulemuse formaat: sõna <tühik> <mitu korda kes-i järel> <mitu korda seesütlevas>

LC_COLLATE=C join -1 2 -2 2 -o 1.1 1.2 2.1 2.2 -a 1 -a 2 -e "###" elusolendid.srt2 seesütlevas.srt2 \
| gawk '$4=="###" || $1 > $3  {print($2 ";" $1 ";" $3)}' \
| sed 's/###/0/' \
> sona_kes_sees.loend

exit

see töötab:
LC_COLLATE=C join -1 2 -2 2 -o 1.1 1.2 2.1 2.2 -a 1 -a 2 -e "###" elusolendid.srt2 seesütlevas.srt2 | gawk  '$4=="###" || ($1 > (10 * $3))  {print}' | grep -v '###' | less

mnjah, milliseid sõnu elusateks pidada? ja mille jaoks? ad jaoks üks loend, ill jaoks teine?
LC_COLLATE=C join -1 2 -2 2 -o 1.1 1.2 2.1 2.2 -a 1 -a 2 -e "###" elusolendid.srt2 seesütlevas.srt2 | gawk  '$4=="###" || ((10 * $3) > $1 && $1 > (4 * $3))  {print}' | grep -v '###' | less

exit
# nende tegemine võtab aega ja ei tea, mis nendega peale hakata
# jätan siia lihtsalt mälestuseks

# sõnad, mis on sisseütlevas käändes
cat ~/svnkrpkirjak/keeleveeb/*.data.idx \
| tr ';\t' '_;' \
| gawk -F ";" '$8 ~ /Ill/ && $7 != "V" {print($5)}' \
| sort | uniq -c | sort -nr \
> sisseütlevas.srt

# sõnad, mis on seestütlevas käändes
cat ~/svnkrpkirjak/keeleveeb/*.data.idx \
| tr ';\t' '_;' \
| gawk -F ";" '$8 ~ /Ela/ && $7 != "V"  {print($5)}' \
| sort | uniq -c | sort -nr \
> seestütlevas.srt

# alaleütlevas
cat ~/svnkrpkirjak/keeleveeb/*.data.idx \
| tr ';\t' '_;' \
| gawk -F ";" '$8 ~ /All/ {print($5)}' \
| sort | uniq -c | sort -nr \
> alaleütlevas.srt

# alalütlevas
cat ~/svnkrpkirjak/keeleveeb/*.data.idx \
| tr ';\t' '_;' \
| gawk -F ";" '$8 ~ /Ade/ {print($5)}' \
| sort | uniq -c | sort -nr \
> alalütlevas.srt

# alaltütlevas
cat ~/svnkrpkirjak/keeleveeb/*.data.idx \
| tr ';\t' '_;' \
| gawk -F ";" '$8 ~ /Abl/ {print($5)}' \
| sort | uniq -c | sort -nr \
> alaltütlevas.srt

# nimetavas
cat ~/svnkrpkirjak/keeleveeb/*.data.idx \
| tr ';\t' '_;' \
| gawk -F ";" '$8 ~ /Nom/ {print($5)}' \
| sort | uniq -c | sort -nr \
> nimetavas.srt

# omastavas
cat ~/svnkrpkirjak/keeleveeb/*.data.idx \
| tr ';\t' '_;' \
| gawk -F ";" '$8 ~ /Gen/ {print($5)}' \
| sort | uniq -c | sort -nr \
> omastavas.srt

# osastavas
cat ~/svnkrpkirjak/keeleveeb/*.data.idx \
| tr ';\t' '_;' \
| gawk -F ";" '$8 ~ /Par/ {print($5)}' \
| sort | uniq -c | sort -nr \
> osastavas.srt

# nende tegemine võtab aega ja ei tea, mis nendega peale hakata
#cat sisseütlevas.srt | LC_COLLATE=C sort -k 2  > seesütlevas.srt2
#cat seestütlevas.srt | LC_COLLATE=C sort -k 2  > seesütlevas.srt2
#cat alaleütlevas.srt | LC_COLLATE=C sort -k 2  > alaleütlevas.srt2
#cat alalütlevas.srt | LC_COLLATE=C sort -k 2  > alalütlevas.srt2
#cat alaltütlevas.srt | LC_COLLATE=C sort -k 2  > alaltütlevas.srt2
#cat nimetavas.srt | LC_COLLATE=C sort -k 2  > nimetavas.srt2
#cat omastavas.srt | LC_COLLATE=C sort -k 2  > omastavas.srt2
#cat osastavas.srt | LC_COLLATE=C sort -k 2  > osastavas.srt2

