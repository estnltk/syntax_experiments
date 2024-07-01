# - Method for getting nertag of given word from ner layer; if nertag is absent, "OTHER" is returned
def get_ner(ner_layer, word_layer, span):
        nertag = None
        if len(ner_layer) > 0:
            word = word_layer.get(span)
            for n in ner_layer:
                for part in n:
                    if part==word:
                        nertag=n.nertag
        if nertag:
            return nertag
        return 'OTHER'
    

# - Method for getting POS tag(s) of given word from estNTLK morph_analysis layer
def get_POS(word_layer, span):
    infinite_verb_forms = ['da', 'des', 'ma', 'maks', 'mas', 'mast', 'mata', 'nud', 'tav', 'tud', 'v']
    # if POS is ambiguous, only unique tags are kept, e.g. ['V', 'A', 'A'] -> ['V', 'A']
    pos_list = []
    word = word_layer.get(span)
    for i in range(len(word.morph_analysis['partofspeech'])):
        if word.morph_analysis['partofspeech'][i] == 'V':
            if word.morph_analysis['form'][i] in infinite_verb_forms:
                pos_list.append('V_inf')
            elif word.form[i] == 'neg':
                pos_list.append('V_neg')
            else:
                pos_list.append('V_fin')
        else:
            pos_list.append(word.morph_analysis['partofspeech'][i])
    
    if len(pos_list) > 1:
        char_unique = [char for indx, char in enumerate(pos_list) if char not in pos_list[:indx]]
        if len(char_unique) < 2:
            return char_unique[0]
        return '|'.join(char_unique)
    return pos_list[0]