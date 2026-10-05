#!/usr/bin/env python3


import os

from estnltk_core.converters.json_importer import json_to_text
from estnltk.taggers import VabamorfDisambiguator

from methods.tagmap import TAG_MAP
from methods.conx_matching import match_feats


def read_txt_to_list(filename: str) -> list[str]:
    """
    Reads and returns txt-file lines as list of strings.
    """
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f]


def read_texts_from_json(file_path: str, n_files=None) -> list:
    """
    Read and convert all json files in folder to EstNLTK Text-objects.
    """
    texts = []
    for fn in os.listdir(file_path):
        if n_files:
            if len(texts) == n_files:
                break
        texts.append(json_to_text(file=f"{file_path}{fn}"))
    return texts


def get_filtered_list(list1: list, list2: list) -> list:
    """
    Finds and returns elements in the first list that are present in the second list. Keeps duplicates.
    """
    set2 = set(list2)
    
    return [x for x in list1 if x in set2]


def disambiguate_vm_morph(text):
    """
    Disambiguating ambiguous Vabamorf analysis.
    """
    vabamorf_disambiguator = VabamorfDisambiguator()
    
    return vabamorf_disambiguator.retag(text)


def get_conx_head(sentence_words: list, match: dict):
    """
    Finding and returning head member of construction example.
    """
    sorted_conx_ids = sorted([word.id for name, word in match.items()])
    sorted_conx_headids = [word.head for word in sentence_words if word.id in sorted_conx_ids]
    head_id = [i for i, conx_id in enumerate(sorted_conx_headids) if conx_id not in sorted_conx_ids][0]
    head_member_id = sorted_conx_ids[head_id]

    if head_member_id:
        for stanza_word in sentence_words:
            if stanza_word.id == head_member_id:
                return stanza_word
    return None


def get_lowercase(match: dict, member_name: str):
    """
    In case of member word's lemma being in lowercase, returns member word's form in lowercase.
    Otherwise returns member word's form.
    """
    if match[member_name].lemma == match[member_name].lemma.lower():
        return match[member_name].text.lower()
    return match[member_name].text
    

def get_conx_member(match: dict, member_name: str):
    """
    Finds and returns specified member from construction example match.
    """
    return match[member_name]
    

def get_form_code(stanza_word):
    """
    Converting Vabamorf tags to EKILEX tags and returning stanza word as a form code.
    """
    lemma_part = stanza_word.morph_analysis.lemma[0]
    form_part = TAG_MAP[stanza_word.morph_analysis.form[0]]
    pos_part = stanza_word.morph_analysis.partofspeech[0]

    return lemma_part+"_"+form_part+"_"+pos_part


def display_example(idx: int, sentences_words: list, matches: list):
    """
    Displaying by index an example sentence, the construction example and construction example's head member.
    """
    for match in matches[idx]:
        ex = sentences_words[idx]
        sorted_conx_ids = sorted([word.id for name, word in match.items()])
        sorted_conx_headids = [word.head for word in ex if word.id in sorted_conx_ids]
        head_id = [i for i, conx_id in enumerate(sorted_conx_headids) if conx_id not in sorted_conx_ids][0]
        head_member_id = sorted_conx_ids[head_id]

        print(" ".join([word.text for word in ex]))
        print(" ".join([word.text for word in ex if word.id in sorted_conx_ids]))
        print(" ".join([word.text for word in ex if word.id == head_member_id]))
        print()


def get_subtree(stanza_word, subtree=None):
    """
    Finding all children of given stanza word from syntax tree recursively. Returns given stanza word and all it's children as a list
    """
    if subtree is None:
        subtree = []

    subtree.append(stanza_word)
    
    children = stanza_word.children

    for child in children:
        get_subtree(child, subtree)

    return subtree
    