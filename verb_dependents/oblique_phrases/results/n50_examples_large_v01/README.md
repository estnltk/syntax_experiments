## 

note: classification2="UNK" in cases where the phrase is not categorized as (abstract) location, time/event, alive, organization.


- n50_verbcase_label_distribution.csv - Label example counts and percentages. Includes all verb+case from n50 10K example set.

- n50_verbcase_label_dist_unk_below60.csv - Filtering out only cases from n50_verbcase_label_distribution where unk_percent is below 60%.

- n50_verbcase_label_loc_vs_other.csv - Label comparison: loc vs all other labels (actor, time, event, UNK). 

	Based on n50_verbcase_label_distribution.

	For each comparison pair only verb+comp+case where the loc_count>=5, other-label-count>=5 and percentages for both labels are over 30%. 

	Then for each verb+comp+case 5 examples are given for both labels.

- n50_verbcase_label_loc_vs_other_readable_sample - first 100 rows from n50_verbcase_label_loc_vs_other.csv.

- n50_verbcase_label_unk_vs_other.csv - Label comparison: unk vs all other labels (actor, time, event, loc). 

	Based on n50_verbcase_label_dist_unk_below60.

	For each comparison pair only verb+comp+case where the unk_count>=2, other-label-count>=2, unk_percent <=60 and other labels are over 30%. 

	Then for each verb+comp+case 5 examples are given for both labels.

- n50_verbcase_label_unk_vs_other_readable_sample - first 100 rows from n50_verbcase_label_unk_vs_other.csv.




