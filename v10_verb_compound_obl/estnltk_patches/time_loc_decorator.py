import os
import pandas as pd
from estnltk.wordnet import Wordnet


class TimeLocDecorator:
    """
    Decorator for PhraseTagger.
    Marks whether the given OBL phrase refers to a location, time  or neither.
    """

    def __init__(self, time_lemmas_path=None, loc_lemmas_path=None):
        self.wn = Wordnet()
        if time_lemmas_path is None:
            time_lemmas_path = '{}/time_lemmas.csv'.format(os.path.dirname(os.path.abspath(__file__)))
        self.time_lemmas = pd.read_csv(time_lemmas_path, encoding="UTF8")

        if loc_lemmas_path is None:
            loc_lemmas_path = '{}/loc_lemmas.csv'.format(os.path.dirname(os.path.abspath(__file__)))
        self.loc_lemmas = pd.read_csv(loc_lemmas_path, encoding="UTF8")
        
        self.loc_form = ['sg ill', 'sg in', 'sg el', 'sg all', 'sg ad', 'sg abl',
                         'pl ill', 'pl in', 'pl el', 'pl all', 'pl ad', 'pl abl']
        self.loc_wn = ["piirkond", "koht", "äritegevuskoht", "maa", "asula", "tegevusala",
                       "ala", "maa-asula", "eluruum", "rahvusriik", "hoone", "ruum", "maapind",
                       "maa-ala", "mander", "tuba", "asukoht", "linn"]
        self.time_wn = ["kuu", "aasta", "aastaaeg", "ajavahemik", "ajaühik", "nädalapäev", "aeg", "päev"]

        self.verb_obl_loc = [["õppima", "kool", "sg in"], ["kirjutama", "alla", "kool", "sg in"]]

    def __call__(self, text_object, phrase_span, annotations):
        """
        Adds three syntax conservation scores for the shortened sentence.
        Shortened sentence is obtained by removing the phrase in the phrase_span from the text.
        """

        # Extract all of the necessary information from the parameters
        obl_root = annotations['root']
        obl_root_id = annotations['root_id']
        obl_lemma = obl_root.lemma
        obl_form = obl_root.form[0]
        phrase_type = None

        # Check if OBL phrase is in locative case, if not return 'None' type
        if obl_form not in self.loc_form:
            annotations.update({
                'phrase_type': phrase_type})
            return annotations

        # If OBL is in locative case and the lemma is a pre-determined time word, return 'TIME' type
        if obl_form in self.loc_form and obl_lemma in self.time_lemmas:
            phrase_type = "TIME"
            annotations.update({
                "phrase_type": phrase_type})
            return annotations

        # If OBL is in locative case and the lemma is a pre-determined location word, return 'LOC' type
        if obl_form in self.loc_form and obl_lemma in self.loc_lemmas:
            phrase_type = "LOC"
            annotations.update({
                "phrase_type": phrase_type})
            return annotations

        # Find the verb-OBL-case combination. In some cases it is possible to determine whether the
        # OBL phrase is a location based on the verb phrase it is in. If the current phrase is like this
        # return 'LOC' type
        current_head = text_object.head[obl_root_id - 1]
        prev_head = obl_root_id

        while current_head != 0:
            prev_head = current_head
            current_head = text_object.head[current_head - 1]

        verb_lemma = text_object.stanza_syntax.lemma[prev_head - 1]
        verb_obl = [verb_lemma]

        verb_comp = []
        for w in text_object.stanza_syntax:
            if w.head == prev_head and 'compound' in w.deprel:
                verb_comp.append(w.lemma)

        verb_obl.extend(verb_comp)
        verb_obl.extend([obl_lemma, obl_form])

        if verb_obl in self.verb_obl_loc:
            phrase_type = "LOC"
            annotations.update({
                "phrase_type": phrase_type})
            return annotations

        # There are a lot of different words referring to places and it is impossible to create an
        # exhaustive list. The next section combats this issue by finding time and location words
        # based on their hypernyms as these are more broad and thus cover more OBL phrases in a
        # smaller set of words.
        synsets = self.wn[obl_lemma]
        if len(synsets) == 1:
            hypernym = synsets[0].hypernyms
            if len(hypernym) > 0:
                if hypernym[0].literal in self.loc_wn:
                    phrase_type = "LOC"
                if hypernym[0].literal in self.time_wn:
                    phrase_type = "TIME"

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
                phrase_type = "TIME"
            if "LOC" in literal_types and "TIME" not in literal_types:
                phrase_type = "LOC"
            if "TIME" in literal_types and "LOC" in literal_types:
                phrase_type = "INCONCLUSIVE"

        annotations.update({
            "phrase_type": phrase_type})

        return annotations