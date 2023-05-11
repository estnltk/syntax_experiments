from estnltk.wordnet import Wordnet

class ReTagger:
    def __init__(self):
        self.wn = Wordnet()
        self.loc_form = ['sg ill', 'sg in', 'sg el', 'sg all', 'sg ad', 'sg abl',
                'pl ill', 'pl in', 'pl el', 'pl all', 'pl ad', 'pl abl']
        self.loc_wn = ["piirkond", "koht", "äritegevuskoht", "maa", "asula", "tegevusala",
                  "ala", "maa-asula", "eluruum", "rahvusriik", "hoone", "ruum", "maapind",
                  "maa-ala", "mander", "tuba", "asukoht", "linn"]
        self.time_wn = ["kuu", "aasta", "aastaaeg", "ajavahemik", "ajaühik", "nädalapäev", "aeg", "päev"]

    def tag_adverb_type(self, entities):
        entity_tags = []

        for i, entity in enumerate(entities):
            lemma = entity.root.lemma
            form = entity.root.form[0]

            if form not in self.loc_form:
                entity_tags.append((i, entity, None))
                continue

            synsets = self.wn[lemma]
            if len(synsets) == 1:
                hypernym = synsets[0].hypernyms
                if hypernym[0].literal in self.loc_wn:
                    entity_tags.append((i, entity, "LOC"))
                elif hypernym[0].literal in self.time_wn:
                    entity_tags.append((i, entity, "TIME"))
                else:
                    entity_tags.append((i, entity, None))

            else:
                literals = [syns.hypernyms[0].literal for syns in synsets]
                literal_types = []

                for literal in literals:
                    if literal in self.loc_wn:
                        literal_types.append("LOC")
                    elif literal in self.time_wn:
                        literal_types.append("TIME")
                    else:
                        literal_types.append(None)

                if "TIME" in literal_types and "LOC" not in literal_types:
                    entity_tags.append((i, entity, "TIME"))
                if "LOC" in literal_types and "TIME" not in literal_types:
                    entity_tags.append((i, entity, "LOC"))
                if "TIME" in literal_types and "LOC" in literal_types:
                    entity_tags.append((i, entity, "INCONCLUSIVE"))
                if "TIME" not in literal_types and "LOC" not in literal_types:
                    entity_tags.append((i, entity, None))

        return entity_tags
