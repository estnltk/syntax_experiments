from estnltk import Layer

from typing import List, Dict, Optional

# =====================================================
#   Creating syntax sketches
# =====================================================

def subtree_size(heads: List[int], tails: List[int], root: int) -> int:
    """
    Computes the size of the subtree specified by the root node, i.e., the root is included into the subtree.
    Arcs of a tree are specified as head, tail pairs, i.e., tails[i] -> heads[i] is an arc.
    """

    result = 0
    for i, dep_head in enumerate(heads):
        if dep_head == root:
            result += subtree_size(heads, tails, tails[i])
    return result + 1


def clean_clause(clause: Layer) -> Dict[str, list]:
    """
    Removes spurious words from clause and extracts relevant information from other layers.
    Spurious words can occur at the beginning or at the end of the clause:
    * conjunctions
    * punctuation marks

    Returns a dictionary of aligned vectors for clause members:
    * ids       -- token numbers
    * postags   -- part-of-speech tags
    * deprels   -- dependency relations
    * heads     -- head of the node
    * root_loc  -- indices of root nodes
    * wordforms -- complete text
    * lemmas    -- lemma
    * features  -- other syntactic features

    Syntax information is specified as in the syntax tree corresponding to the entire sentence.
    As clause finding algorithm is not perfect there can be several roots in the clause.
    The information about root can be found by fetching the corresponding field, e.g. ids[root_loc[0]].
    These fields contain enough information to store the cleaned clause in the conll-format
    """

    # Extract relevant fields
    ids = list(clause.ud_syntax.id)
    postags = list(clause.ud_syntax.xpostag)
    deprels = list(clause.ud_syntax.deprel)
    heads = list(clause.ud_syntax.head)

    wordforms = list(clause.ud_syntax.text)
    lemmas = list(clause.ud_syntax.lemma)
    features = list(clause.ud_syntax.feats)

    # Remove leading punctuation marks and conjunction
    while postags and ('J' in postags[0] or 'Z' in postags[0]):
        heads.pop(0)
        ids.pop(0)
        deprels.pop(0)
        postags.pop(0)
        wordforms.pop(0)
        lemmas.pop(0)
        features.pop(0)

    if not postags:
        return dict(ids=[], postags=[], deprels=[], heads=[], root_loc=[], wordforms=[], lemmas=[], features=[])

    # Remove trailing punctuation marks and conjunction
    while 'J' in postags[-1] or 'Z' in postags[-1]:
        heads.pop()
        ids.pop()
        deprels.pop()
        postags.pop()
        wordforms.pop()
        lemmas.pop()
        features.pop()

    # Find indices of root nodes
    root_locations = [i for i, head in enumerate(heads) if head not in ids]

    return dict(
        ids=ids, postags=postags, deprels=deprels, heads=heads,
        root_loc=root_locations,
        wordforms=wordforms, lemmas=lemmas, features=features)


def syntax_sketch(clause: Dict[str, list], ordered=True):
    """
    Computes syntax sketch for a clause that encodes information about the root node and the first level child nodes.
    By default the first level child nodes are lexicographically ordered in the sketch.
    
    Examples:
    
    wordforms: ['Ma', 'kaldun', 'arvama']
    ids:       [1, 2, 3]
    heads:     [2, 0, 2]
    postags:   ['P', 'V', 'V']
    deprels:   ['nsubj', 'root', 'xcomp']
    root_loc:  [1]
    output:    '[V]nsubj(L)xcomp(L)'

    wordforms: ['Vermeeri', 'saatus', 'oli', 'teistsugune']
    ids:       [6, 7, 8, 9]
    heads:     [7, 9, 9, 3]
    postags:   ['S', 'S', 'V', 'P']
    deprels:   ['nmod', 'nsubj:cop', 'cop', 'ccomp']
    root_loc:  [3]
    output:    '[S]cop(L)nsubj:cop(L)'
    
    wordforms: ['uus', 'ooper', 'tuleb', 'habras', 'ja', 'ilus']
    ids:       [8, 9, 10, 11, 12, 13]
    heads:     [9, 10, 2, 10, 13, 11]
    postags:   ['A', 'S', 'V', 'A', 'J', 'A']
    deprels:   ['amod', 'nsubj', 'ccomp', 'xcomp', 'cc', 'conj']
    root_loc:  [2]
    output:    '[V]nsubj(L)xcomp(P)'
    """

    assert len(clause['root_loc']) == 1, "The clause must have a single root"

    # Compute root tag for the sketch
    root_tag = clause['postags'][clause['root_loc'][0]]
    if root_tag == 'V':
        # group of verbs
        sketch_root = 'V'
    elif root_tag in ['S', 'P', 'A', 'Y', 'N']:
        # non-verbs: substantives, pronouns, adjectives,
        # acronyms/abbreviations, numerals
        sketch_root = 'S'
    else:
        # remaining postags
        sketch_root = 'X'

    # Compute sketches for child nodes
    first_level = list()
    root = clause['ids'][clause['root_loc'][0]]
    for i, head in enumerate(clause['heads']):
        if head != root:
            continue

        length = subtree_size(clause['heads'], clause['ids'], clause['ids'][i])
        if length < 3:
            subtree_cat = 'L'
        elif length < 10:
            subtree_cat = 'P'
        else:
            subtree_cat = 'ÜP'

        subtree = clause['deprels'][i] + '({})'.format(subtree_cat)
        first_level.append(subtree)

    if ordered:
        return '[{root}]{children}'.format(root=sketch_root, children=''.join(sorted(first_level)))
    else:
        return '[{root}]{children}'.format(root=sketch_root, children=''.join(first_level))


# =====================================================
#   Filtering lists of clauses by sketches
# =====================================================

def extract_sketches(clause_conllus: List[str], clause_dicts: List[Dict[str, list]], 
                     target_sketch:str, amount:Optional[int]=None, verbose:bool=False):
    '''
    Extracts given amount of target_sketch from clause_conllus and clause_dicts. 
    Returns extracted items. 
    If amount is None (default), then extracts all clauses corresponding to the sketch.
    Returns triple: (extracted_conllus, extracted_dicts, number_of_extracted_items)
    '''
    assert len(clause_conllus) == len(clause_dicts), \
        'Unexpectedly, numers of conllu clauses and corresponding clause dicts differ: '+\
        f' {len(clause_conllus)} vs {len(clause_dicts)}'
    extracted = []
    extracted_dicts = []
    for clause_id, clause_conllu in enumerate(clause_conllus):
        clause_dict = clause_dicts[clause_id]
        sketch = syntax_sketch(clause_dict)
        if sketch == target_sketch:
            if amount is None or len(extracted) < amount:
                extracted.append( clause_conllu )
                extracted_dicts.append( clause_dict )
    if verbose:
        print('Extracted {} instances of sketch {}'. format(len(extracted), target_sketch))
    return extracted, extracted_dicts, len(extracted)


def remove_sketches(clause_conllus: List[str], clause_dicts: List[Dict[str, list]], 
                    target_sketch:str, amount:Optional[int]=None, verbose:bool=False):
    '''
    Removes given amount of target_sketch from clause_conllus and clause_dicts. 
    Returns preserved items (and count of removed items). 
    If amount is None (default), then removes all clauses corresponding to the sketch.
    Returns triple: (preserved_conllus, preserved_dicts, number_of_removed_items)
    '''
    assert len(clause_conllus) == len(clause_dicts), \
        'Unexpectedly, numers of conllu clauses and corresponding clause dicts differ: '+\
        f' {len(clause_conllus)} vs {len(clause_dicts)}'
    preserved = []
    preserved_dicts = []
    removed = 0
    for clause_id, clause_conllu in enumerate(clause_conllus):
        clause_dict = clause_dicts[clause_id]
        sketch = syntax_sketch(clause_dict)
        if sketch == target_sketch:
            if amount is None or removed < amount:
                removed += 1
                continue
        preserved.append( clause_conllu )
        preserved_dicts.append( clause_dict )
    if verbose:
        print('Removed {} instances of sketch {}'. format(removed, target_sketch))
    return preserved, preserved_dicts, removed