# creates and returns POS-sequence of Text object as string
def get_POS_sequence(text_obj):
    pos_list = [pos for pos in text_obj.morph_analysis.partofspeech]
    pos_string = ""
    for i, char_list in enumerate(pos_list):
        if len(char_list) < 2:
            if i < len(pos_list) - 1:
                pos_string+=char_list[0]+"-"
            else:
                pos_string+=char_list[0]
        else:
            # keeps only unique POS tags when POS is ambiguous, e.g. ['V', 'A', 'A'] -> ['V', 'A']
            char_unique = [char for indx, char in enumerate(char_list) if char not in char_list[:indx]]
            if len(char_unique) == 1:
                if i < len(pos_list) - 1:
                    pos_string+=char_unique[0]+"-"
                else:
                    pos_string+=char_unique[0]
            else:
                pos_string+="("
                for j, char in enumerate(char_unique):
                    if j == len(char_unique) - 1:
                        if i < len(pos_list) - 1:
                            pos_string+=char+")-"
                        else:
                            pos_string+=char+")"
                    else:
                        pos_string+=char+"|"
    return pos_string

# creates and returns POS-sequence of Text object as string, with added verb information
def get_POS_sequence_with_verb_info(text_obj):
    infinite_verb_forms = ['da', 'des', 'ma', 'maks', 'mas', 'mast', 'mata', 'nud', 'tav', 'tud', 'v']
    
    pos_list = []
    for word in text_obj.morph_analysis:
        if 'V' in word.partofspeech:
            temp = []
            for i in range(len(word.partofspeech)):
                if word.partofspeech[i] == 'V':
                    if word.form[i] in infinite_verb_forms:
                        temp.append('V_inf')
                    elif word.form[i] == 'neg':
                        temp.append('V_neg')
                    else:
                        temp.append('V_fin')
                else:
                    temp.append(word.partofspeech[i])
            pos_list.append(temp)
        else:
            pos_list.append(word.partofspeech)
            
    pos_string = ""
    for i, char_list in enumerate(pos_list):
        if len(char_list) < 2:
            if i < len(pos_list) - 1:
                pos_string+=char_list[0]+"-"
            else:
                pos_string+=char_list[0]
        else:
            # keeps only unique POS tags when POS is ambiguous, e.g. ['V', 'A', 'A'] -> ['V', 'A']
            char_unique = [char for indx, char in enumerate(char_list) if char not in char_list[:indx]]
            if len(char_unique) == 1:
                if i < len(pos_list) - 1:
                    pos_string+=char_unique[0]+"-"
                else:
                    pos_string+=char_unique[0]
            else:
                pos_string+="("
                for j, char in enumerate(char_unique):
                    if j == len(char_unique) - 1:
                        if i < len(pos_list) - 1:
                            pos_string+=char+")-"
                        else:
                            pos_string+=char+")"
                    else:
                        pos_string+=char+"|"
    return pos_string