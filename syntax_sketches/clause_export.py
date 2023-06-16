from typing import Dict, List


def export_cleaned_clause(clause: Dict[str, list]) -> str:
    """
    Exports a cleaned clause into the CoNLL-U format. This can be used to create various data sets.
    The function assumes that the input is generated by the function clean_clause and that there is only one root node.
    Returns a properly formatted table where each token is on the separate line and upos and xpos fields are the same.
    """

    assert len(clause['root_loc']) == 1, 'There can be only one root in a clause'
    assert len(clause['ids']) == len(clause['wordforms']) == len(clause['lemmas']), 'Fields must be aligned'
    assert len(clause['ids']) == len(clause['postags']) == len(clause['features']), 'Fields must be aligned'
    assert len(clause['ids']) == len(clause['deprels']) == len(clause['heads']), 'Fields must be aligned'

    # As standard ids will be assigned to all tokens in a clause we need update heads
    head_map = {clause_id: idx + 1 for idx, clause_id in enumerate(clause['ids'])}
    
    result = []
    row_template = '{id}\t{wordform}\t{lemma}\t{postag}\t{postag}\t{features}\t{head}\t{deprel}\t_\t_'
    for i in range(len(clause['ids'])):

        head = head_map.get(clause['heads'][i], 0)
        deprel = clause['deprels'][i] if head != 0 else 'root'

        if clause['features'][i]:
            features = '|'.join([key + '=' + value for key, value in clause['features'][i].items()])
        else:
            features = '_'

        result.append(row_template.format(
            id=i + 1,
            wordform=clause['wordforms'][i],
            lemma=clause['lemmas'][i],
            postag=clause['postags'][i],
            features=features,
            head=head,
            deprel=deprel))

    return '\n'.join(result)



def remove_extracted_from_conllu_and_dicts(overall_conllu: List[str], 
                                           overall_dicts: List[Dict[str, list]], 
                                           extracted_conllu: List[str]):
    '''
    Removes items of extracted_conllu from overall_conllu (and from corresponding 
    overall_dicts).
    
    Assumes that overall_conllu and extracted_conllu are lists of CoNLL-U format 
    clause strings, and that extracted_conllu is a sub list of overall_conllu.
    overall_dicts should be a list of dictionaries with CoNLL features, each dict
    corresponding to a clause with the same index in overall_conllu.
    
    Note that there can be repeating clauses in overall_conllu, e.g. clause "ma ei tea"
    ('I don't know') may appear multiple times. If a repeating clause appears in 
    extracted_conllu, all of its instances will be deleted from overall_conllu and 
    overall_dicts.
    This function keeps track of how many times each clause (conllu) was deleted and 
    returns a dictionary mapping extracted clause conllu-s to corresponding deletion 
    counts (for debugging purposes).
    
    Returns (new_clause_conllu, new_clause_dicts, deletion_counts)
    '''
    assert len(overall_conllu) == len(overall_dicts)
    new_clause_conllu = []
    new_clause_dicts = []
    deletion_counts = dict()
    extracted_counts = \
        {conllu: extracted_conllu.count(conllu) for conllu in extracted_conllu}
    for cid, conllu in enumerate(overall_conllu):
        if conllu not in extracted_conllu:
            # Preserve clause
            new_clause_conllu.append(conllu)
            new_clause_dicts.append(overall_dicts[cid])
        else:
            # Delete clause
            # Keep track of how many times clause was deleted
            if conllu not in deletion_counts:
                deletion_counts[conllu] = 0
            deletion_counts[conllu] += 1
    return new_clause_conllu, new_clause_dicts, deletion_counts