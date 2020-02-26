import os
from typing import List

from estnltk import ElementaryBaseSpan, Annotation, Layer, Text


def conllu_file_to_texts_list(file: str, layer_name: str = 'syntax_gold') -> List[Text]:
    """
    Takesn in file in conll-u format and returns list of texts with the syntax_gold layer
    :param file: conll-u format file
    :param layer_name: layer name for the conllu syntax
    :return: list of texts
    """
    texts = []
    sentence = []
    added = False
    with open(file, 'r', encoding='utf-8') as f:
        start = 0
        doc = file.split('.')[0]
        for line_nr, line in enumerate(f):

            if 'sent_id' in line:
                doc = '_'.join(line.split(' ')[-1].split('_')[0:2])
                sent_id = line.split(' ')[-1].split('_')[-1].strip()
                added = False
            elif '#' in line:
                sent_id = str(line_nr)
                added = False
                text = Text()
                words = Layer(name='words',
                              text_object=text,
                              attributes=[],
                              ambiguous=True
                              )
                sentences = Layer(name='sentences',
                                  text_object=text,
                                  attributes=[],
                                  enveloping='words',
                                  ambiguous=False
                                  )
                normal_attributes = ['id', 'form', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps',
                                     'misc']
                syntax = Layer(name=layer_name, attributes=normal_attributes, text_object=text)
                compound_tokens = Layer(name='compound_tokens', attributes=['type', 'normalized'], text_object=text)


            elif line != '#\n' and line != '\n' and line != '':
                l = line.strip().split('\t')

                ID = l[0]
                form = l[1]
                lemma = l[2]
                upos = l[3]
                xpos = l[4]
                feats = l[5]
                head = l[6]
                deprel = l[7]
                deps = l[8]
                misc = l[9].strip()
                sentence.append(form)
                base_span = ElementaryBaseSpan(start, start + len(form))
                attributes = {'id': ID, 'form': form, 'lemma': lemma, 'upostag': upos, 'xpostag': xpos, 'feats': feats,
                              'head': head, 'deprel': deprel, 'deps': deps, 'misc': misc}
                annotations = Annotation(base_span, **attributes)
                syntax.add_annotation(base_span, **annotations)

                words.add_annotation(base_span)
                start += len(form) + 1

            elif line == '\n' and not added:

                try:
                    text.text = ' '.join(sentence)
                    sentence = []
                    sentences.add_annotation(words)
                    text.add_layer(words)
                    text.add_layer(compound_tokens)
                    text.add_layer(sentences)
                    text.add_layer(syntax)
                    text.meta = {'doc': doc, 'chunk': sent_id}
                    texts.append(text)
                    added = True
                    start = 0
                except Exception as e:
                    print('Couldn\'t add layers to text: ' + text.text + e)
    if not added:

        try:
            sentences.add_annotation(words)
            text.add_layer(words)
            text.add_layer(sentences)
            text.add_layer(syntax)
            text.add_layer(compound_tokens)
            text.meta = {'doc': doc, 'chunk': sent_id}
            texts.append(text)

        except:
            print("Couldn't add layers to text: " + text.text)

    return texts


def conllu_files_to_text_list(folder: str, layer_name: str = 'syntax_gold') -> List[Text]:
    texts = []
    for file in os.listdir(folder):
        texts.extend(conllu_file_to_texts_list(file=folder + '/' + file, layer_name=layer_name))

    return texts
