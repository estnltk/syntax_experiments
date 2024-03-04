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