from vabamorf_2_neural import neural_model_tags
# või installida estnltk_neural 1.7.3 ja importida otse seal
# from estnltk_neural.taggers.neural_morph.new_neural_morph.vabamorf_2_neural import neural_model_tags


from typing import List


def get_cg_case(analysis):
    """
    analysis
    """
    for s1 in neural_model_tags(
        word="viis", pos=analysis["partofspeech"], form=analysis["form"]
    ):
        for s2 in s1.split("|"):
            if s2.startswith("CASE="):
                return s2.split("=")[1]

    return None


def collect_misanalysed_transactions(
    pat_ids: List[int], patterns: dict, transactions_raw: List[dict]
):

    misanalysed_transactions = {pat_id: [] for pat_id in pat_ids}

    # Potential analysis errors
    for head_id, transaction_rows in transactions_raw.items():
        cases = [tr["case"] for tr in transaction_rows]
        adps = [
            tr["frequent_form"] for tr in transaction_rows if tr["deprel"] == "case"
        ]
        inf_verbs = [
            tr["frequent_form"]
            for tr in transaction_rows
            if "sup" in tr["feats"].split(",") or "inf" in tr["feats"].split(",")
        ]

        for pat_id in pat_ids:
            adp_matched = not patterns[pat_id]["adp"] or patterns[pat_id]["adp"] in adps
            inf_verbs_matched = (
                not patterns[pat_id]["inf_verb"]
                or patterns[pat_id]["inf_verb"] in inf_verbs
            )
            case_matched = patterns[pat_id]["phrase_case"] in cases

            if adp_matched and inf_verbs_matched and not case_matched:
                misanalysed_transactions[pat_id].append(head_id)
    return misanalysed_transactions
