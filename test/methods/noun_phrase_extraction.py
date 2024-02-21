# -- imports
from estnltk import Text
from estnltk.taggers.standard.syntax.phrase_extraction.phrase_extractor import PhraseExtractor
from estnltk_neural.taggers import StanzaSyntaxTagger
from estnltk.taggers import NerTagger
import pandas as pd

# -- initializing phrase extractors for different noun phrase types
#
# decorator for filtering out noun phrases that don't have noun as root
def partofspeech_filter(text, span, annotation):
    if annotation['root']['upostag'] != 'S':
        return None
    return annotation

# head is obl
obl_phrase_extractor = PhraseExtractor(deprel="obl", syntax_layer="stanza_syntax",
                                   output_layer="obl_phrases")
# head is nsubj
nsubj_phrase_extractor = PhraseExtractor(deprel="nsubj", syntax_layer="stanza_syntax",
                                   output_layer="nsubj_phrases")
# head is nsubj of copula sentence
nsubj_cop_phrase_extractor = PhraseExtractor(deprel="nsubj:cop", syntax_layer="stanza_syntax",
                                   output_layer="nsubj_cop_phrases")
# head is obj
obj_phrase_extractor = PhraseExtractor(deprel="obj", syntax_layer="stanza_syntax",
                                   output_layer="obj_phrases")
# head is xcomp (only if noun)
xcomp_phrase_extractor = PhraseExtractor(decorator=partofspeech_filter, deprel="xcomp", syntax_layer="stanza_syntax",
                                        output_layer="xcomp_phrases")


# -- initializing StanzaSyntaxtagger()
stanza_tagger = StanzaSyntaxTagger(input_type='morph_analysis', input_morph_layer='morph_analysis',
                                   add_parent_and_children=True)

# -- initializing NerTagger
ner_tagger = NerTagger()

# -- creating DataFrame
df = pd.DataFrame(columns=['phrase', 'text_id', 'start_end', 'phrase_type', 'has_ner_entity', 'has_timex_entity'])

# tags and returns noun phrases in input text
def extract_noun_phrases(text_obj):
    obl_phrase_extractor.tag( text_obj )
    nsubj_phrase_extractor.tag( text_obj )
    nsubj_cop_phrase_extractor.tag( text_obj )
    obj_phrase_extractor.tag( text_obj )
    xcomp_phrase_extractor.tag( text_obj )
    return text_obj.obl_phrases, text_obj.nsubj_phrases, text_obj.nsubj_cop_phrases, text_obj.obj_phrases, text_obj.xcomp_phrases

# creates EstNLTK Text-objects from noun phrase layers
def create_Text_objects(text_id, phrase_type, phrase_layer):
    text_objects = []
    for phrase in phrase_layer:
        phrase_string = " ".join(phrase.text)
        text_obj = Text(phrase_string).tag_layer(['morph_analysis', 'timexes'])
        text_obj.meta['phrase_type'] = phrase_type
        text_obj.meta['text_id'] = text_id
        text_obj.meta['start_end'] = tuple([phrase.start, phrase.end])
        ner_tagger.tag(text_obj)
        stanza_tagger.tag(text_obj)
        text_objects.append(text_obj)
    return text_objects

# helper function for noun_phrases_to_df, iterates over data and appends to DataFrame
def append_data_to_df(all_phrase_text_objects):
    global df
    for phrase in all_phrase_text_objects:
        # -- 0 -> false
        # -- 1 -> true
        has_ner_entity = 0
        has_timex_entity = 0
        if phrase.ner:
            has_ner_entity = 1
        elif phrase.timexes:
            has_timex_entity = 1
        temp_data = {'phrase': phrase, 'text_id': phrase.meta['text_id'], 'start_end': phrase.meta['start_end'], 'phrase_type': phrase.meta['phrase_type'], 
                     'has_ner_entity': has_ner_entity, 'has_timex_entity': has_timex_entity}
        temp = pd.DataFrame.from_records([temp_data])
        df = pd.concat([df, temp], ignore_index=True)
    return df
            
# appends phrases to DataFrame    
def create_df(text_id, text_obj):
    text_obj.meta['text_id'] = text_id
    obl_phrases, nsubj_phrases, nsubj_cop_phrases, obj_phrases, xcomp_phrases = extract_noun_phrases(text_obj)
    obl_phrase_texts = create_Text_objects(text_id, 'obl_phrase', obl_phrases)
    nsubj_phrase_texts = create_Text_objects(text_id, 'nsubj_phrase', nsubj_phrases)
    nsubj_cop_phrase_texts = create_Text_objects(text_id, 'nsubj_cop_phrase', nsubj_cop_phrases)
    obj_phrase_texts = create_Text_objects(text_id, 'obj_phrase', obj_phrases)
    xcomp_phrase_texts = create_Text_objects(text_id, 'xcomp_phrase', xcomp_phrases)
    return append_data_to_df(obl_phrase_texts+nsubj_phrase_texts+nsubj_cop_phrase_texts+obj_phrase_texts+xcomp_phrase_texts)
