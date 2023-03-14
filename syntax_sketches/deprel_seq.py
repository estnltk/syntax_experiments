import conllu

def collect_deprel_seqs(in_file: str):
    '''
    Reads sentences from given conllu file (`in_file`) and 
    collects all `deprel` sequences corresponding to sentences. 
    Returns a list of sentences, each sentence represented as 
    a `deprel` sequence string, where word `deprels` are joined 
    via `|`.
    This function is used only for data exploration.
    '''
    with open(in_file, 'r', encoding='utf-8') as input_file:
        conll_sentences = conllu.parse(input_file.read())
    all_deprel_seqs = []
    for sentence in conll_sentences:
        deprel_seq = []
        for token in sentence:
            deprel_seq.append(token["deprel"])
        all_deprel_seqs.append('|'.join(deprel_seq))
    return all_deprel_seqs