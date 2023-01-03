

obl näitelausete saamine:

5000 tektsiga korpus -> eraldi lausetena salvestatud kollektsiooni

30 (protsenti), seed väärtusega 12345 ja laused kus on 1 obl

>> python 4_export_2_labelstudio.py obl conf.ini sample1000_one_obl.json 30 12345 1


| obl| count| 
|:-------|:---|
| free entity  | 595     | 
| bound entity     | 225    |
| unnatural sentences    | 175     |
| not correct entity    | 5     |


| obl| free entity | bound entity |
|:-------|:---|:---|
| conserved        | 448    | 139   |
| unconserved    | 147     | 86  |

