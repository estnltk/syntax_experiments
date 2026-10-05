#!/usr/bin/env python3

# Finding pattern matches from syntax dependency-tree of a sentence

# Requirements: EstNLTK 1.7.2+

import re


def match_deprels(word, feats: dict) -> bool:
    if feats.get("deprels") and word.deprel not in feats["deprels"]:
        return False
    return True

def match_partofspeeches(word, feats: dict) -> bool:
    if feats.get("partofspeeches") and word.morph_analysis.partofspeech[0] not in feats["partofspeeches"]:
        return False
    return True

def match_forms(word, feats: dict) -> bool:
    if feats.get("forms") and len([form for form in feats["forms"] if form == word.morph_analysis.form[0]]) == 0:
        return False
    return True

def match_lemmas_old(word, feats: dict) -> bool:
    if feats.get("lemmas") and word.morph_analysis.lemma[0] not in feats["lemmas"]:
        return False
    return True

def match_lemmas(word, feats: dict) -> bool:
    """
    Matching lemmas based on full string or regex pattern.
    """
    lemma = word.morph_analysis.lemma[0]

    exact_lemmas = feats.get("lemmas")
    regex_lemmas = feats.get("lemma_regex")

    if exact_lemmas:
        if lemma not in exact_lemmas:
            return False

    if regex_lemmas:
        if not any(
            re.search(pattern, lemma)
            for pattern in regex_lemmas
        ):
            return False

    return True

def match_instances(word, feats: dict) -> bool:
    if feats.get("instances") and word.text.lower() not in feats["instances"]:
        return False
    return True


def match_feats(word, feats: dict) -> bool:
    """
    Matching feats, all must be True
    """
    if match_deprels(word, feats)\
          and match_partofspeeches(word, feats)\
              and match_forms(word, feats)\
                and match_lemmas(word, feats)\
                    and match_instances(word, feats):
        return True
    return False


def match_restriction_feats(word, feats: dict) -> bool:
    """
    Matching restriction feats. Either all node restriction, node parent's restriction or node child's restriction feats have to be True.

    {
    "deprels": list[str] | None,
    "partofspeeches": list[str] | None,
    "forms": list[str] | None,
    "lemmas": list[str] | None,
    "lemma_regex": list[str] | None,
    "instance": list[str] | None,
    "parent": {
        "deprels": list[str] | None,
        "partofspeeches": list[str] | None,
        "forms": list[str] | None,
        "lemmas": list[str] | None,
        "lemma_regex": list[str] | None,
        "instances": list[str] | None
        } | None,
    "child": dict | None
    }
    """
    if feats is None:
        return False
    
    # feats that apply directly to the node
    direct_feat_names = {
        "deprels",
        "partofspeeches",
        "forms",
        "lemmas",
        "lemma_regex",
        "instances"
    }
    direct_feats = {
        key: feats.get(key)
        for key in direct_feat_names
    }
    if any(value is not None for value in direct_feats.values()):
        if match_feats(word, direct_feats):
            return True
        
    if feats.get("parent") and word.parent_span:
        if match_feats(word.parent_span, feats.get("parent")):
            return True
    if feats.get("child") and len(word.children) > 0:
        for child in word.children:
            if match_feats(child, feats.get("child")):
                return True
    return False


def check_order(match, order_rules):
    for first, relation, second in order_rules:
        first_word = match[first]
        second_word = match[second]
        if relation == "BEFORE":
            if first_word.id >= second_word.id:
                return False
        elif relation == "AFTER":
            if first_word.id <= second_word.id:
                return False
    return True


def get_pattern(stanza_words: list, pattern: dict, anchor_name: str):
    """
    Finds syntax dependency-tree structures matching a pattern. 
    Handles both linear structures and branching.

    Input pattern includes:
        - member nodes (required),
        - member node restrictions (optional),
        - edges (required),
        - member ordering (optional).
    
    nodes: member nodes and their features.
    
    node_restricions: member node restrictions regarding their heads and/or dependents outside the pattern can be specified in their features.

    edges: node edges determine dependency relations between member nodes, whether the structure is linear or branching.
        NB! For each edge, first member is head and second member its dependent.

    order: member node order can be specified.

    Pattern attribute structure:

    pattern = {
        "nodes": {
            "A": {
                "deprels": list[str] | None,
                "partofspeeches": list[str] | None,
                "forms": list[str] | None,
                "lemmas": list[str] | None,
                "lemma_regex": list[str] | None,
                "instances": list[str] | None
                },
            "B": {...features...},
            "C": {...features...}
        },
        "node_restrictions": {
            "A": {...features...} | None,
            "B": {
                "deprels": list[str] | None,
                "partofspeeches": list[str] | None,
                "forms": list[str] | None,
                "lemmas": list[str] | None,
                "lemma_regex": list[str] | None,
                "instances": list[str] | None,
                "parent": {"deprels": list[str] | None,
                            "partofspeeches": list[str] | None,
                            "forms": list[str] | None,
                            "lemmas": list[str] | None,
                            "lemma_regex": list[str] | None,
                            "instances": list[str] | None
                            } | None,
                "child": {...features...} | None
            },
            "C": {...features...} | None
        } | None,
        "edges": [
            ("A", "B"),  # A is head of B
            ("A", "C")   # A is head of C
        ],
        "order": [
            ("A", "BEFORE", "B"),
            ("C", "AFTER", "A")
        ] | None
    }

    anchor_name: name of the node from which matching starts, always the highest node on syntax tree.
    """

    children = {}

    for w in stanza_words:
        children.setdefault(w.head, []).append(w)

    node_feats = pattern["nodes"]
    node_restriction_feats = pattern.get("node_restrictions", {})
    edges = pattern["edges"]
    order = pattern.get("order")

    # which pattern nodes must be children of each pattern node
    pattern_children = {}

    for parent, child in edges:
        pattern_children.setdefault(parent, []).append(child)

    matches = []

    anchors = [
        w for w in stanza_words
        if match_feats(w, node_feats[anchor_name])\
              and not match_restriction_feats(w, node_restriction_feats[anchor_name])
    ]

    def expand(pattern_node, word, current_match):
        """
        Trying to recursively match all descendants required by
        pattern_node.
        """

        required_children = pattern_children.get(pattern_node, [])

        # leaf in the pattern
        if not required_children:
            return [current_match]

        results = []

        def match_required_child(index, partial_match):
            if index == len(required_children):
                results.append(partial_match.copy())
                return
            child_name = required_children[index]
            expected_feats = node_feats[child_name]
            expected_restriction_feats = node_restriction_feats[child_name]

            for candidate in children.get(word.id, []):

                # the same sentence token will not be reused
                if candidate in partial_match.values():
                    continue

                if not match_feats(candidate, expected_feats):
                    continue

                if match_restriction_feats(candidate, expected_restriction_feats):
                    continue

                new_match = partial_match.copy()
                new_match[child_name] = candidate

                child_results = expand(
                    child_name,
                    candidate,
                    new_match
                )

                for child_result in child_results:
                    match_required_child(
                        index + 1,
                        child_result
                    )

        match_required_child(0, current_match)

        return results

    # finding pattern matches for each anchor
    for anchor in anchors:
        initial_match = {anchor_name: anchor}

        found_matches = expand(anchor_name, anchor, initial_match)

        # checking pattern match member order, if order has been specified for some or all members
        if order:
            for found_match in found_matches:
                if check_order(found_match, order):
                    matches.append(found_match)
        else:
            matches.extend(found_matches)

    return matches
