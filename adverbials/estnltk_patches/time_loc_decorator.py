import os
import pandas as pd
from estnltk.wordnet import Wordnet


class TimeLocDecorator:
    """
    Decorator for PhraseTagger.
    Marks whether the given OBL phrase refers to a location, time  or neither.
    """

    def __init__(self):
        self.wn = Wordnet()
        time_lemmas_path = '{}/time_lemmas.csv'.format(os.path.dirname(os.path.abspath(__file__)))
        self.time_lemmas = pd.read_csv(time_lemmas_path, encoding="UTF8")
        loc_lemmas_path = '{}/loc_lemmas.csv'.format(os.path.dirname(os.path.abspath(__file__)))
        self.loc_lemmas = pd.read_csv(loc_lemmas_path, encoding="UTF8")
        self.loc_form = ['sg ill', 'sg in', 'sg el', 'sg all', 'sg ad', 'sg abl',
                         'pl ill', 'pl in', 'pl el', 'pl all', 'pl ad', 'pl abl']
        self.loc_wn = ["piirkond", "koht", "äritegevuskoht", "maa", "asula", "tegevusala",
                       "ala", "maa-asula", "eluruum", "rahvusriik", "hoone", "ruum", "maapind",
                       "maa-ala", "mander", "tuba", "asukoht", "linn"]
        self.time_wn = ["kuu", "aasta", "aastaaeg", "ajavahemik", "ajaühik", "nädalapäev", "aeg", "päev"]

    def __call__(self, text_object, phrase_span, annotations):
        """
        Adds three syntax conservation scores for the shortened sentence.
        Shortened sentence is obtained by removing the phrase in the phrase_span from the text.
        """
        obl_root = annotations['root']
        obl_lemma = obl_root.lemma
        obl_form = obl_root.form[0]
        obl_type = None

        if obl_form not in self.loc_form:
            annotations.update({
                'obl_type': obl_type})
            return annotations

        if obl_form in self.loc_form and obl_lemma in self.time_lemmas:
            obl_type = "TIME"
            annotations.update({
                "obl_type": obl_type})
            return annotations

        if obl_form in self.loc_form and obl_lemma in self.loc_lemmas:
            obl_type = "LOC"
            annotations.update({
                "obl_type": obl_type})
            return annotations

        synsets = self.wn[obl_lemma]
        if len(synsets) == 1:
            hypernym = synsets[0].hypernyms
            if len(hypernym) > 0:
                if hypernym[0].literal in self.loc_wn:
                    obl_type = "LOC"
                if hypernym[0].literal in self.time_wn:
                    obl_type = "TIME"

        else:
            literals = [syns.hypernyms[0].literal if len(syns.hypernyms) >= 1 else None for syns in synsets]
            literal_types = []

            for literal in literals:
                if literal in self.loc_wn:
                    literal_types.append("LOC")
                elif literal in self.time_wn:
                    literal_types.append("TIME")
                else:
                    literal_types.append(None)

            if "TIME" in literal_types and "LOC" not in literal_types:
                obl_type = "TIME"
            if "LOC" in literal_types and "TIME" not in literal_types:
                obl_type = "LOC"
            if "TIME" in literal_types and "LOC" in literal_types:
                obl_type = "INCONCLUSIVE"

        annotations.update({
            "obl_type": obl_type})

        return annotations
