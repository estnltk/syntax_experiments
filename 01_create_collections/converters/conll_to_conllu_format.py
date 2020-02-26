from typing import List

from estnltk import Text, Layer, ElementaryBaseSpan, Annotation


def conll_to_conllu_text_list(file: str, layer_name: str = "syntax_gold") -> List[Text]:
    """
    Takesn in file in conll-x format and returns list of texts with the conll-u formatted syntax layer
    :param file: conll-x format file
    :param layer_name: layer name for the syntax gold
    :return: list of texts
    """
    texts = []
    document = file.split('/')[-1]
    doc_info = '_'.join(document.split('.')[0].split('_')[0:4])
    chunk = file.split('.inforem')[0].split('_')[-1]
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
    normal_attributes = ['id', 'form', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc']
    syntax = Layer(name=layer_name, attributes=normal_attributes, text_object=text)
    compound_tokens = Layer(name='compound_tokens', attributes=['type', 'normalized'], text_object=text)
    start = 0
    sentence = []
    with open(file, 'r', encoding='utf-8') as f:
        for line in f:

            if line != '\n':
                l = line.split('\t')
                id = l[0]
                form = l[1]
                lemma = l[2]
                upos = l[3]
                xpos = l[4]
                feats = l[5]
                head = l[6] if l[6] != '333' else '33'
                deprel = l[7] if l[7] != 'ROOT' else 'root'
                deps = l[8]
                misc = l[9].strip()
                sentence.append(form)
                base_span = ElementaryBaseSpan(start, start + len(form))
                attributes = {'id': id, 'form': form, 'lemma': lemma, 'upostag': upos, 'xpostag': xpos, 'feats': feats,
                              'head': head, 'deprel': deprel, 'deps': deps, 'misc': misc}
                annotations = Annotation(base_span, **attributes)
                syntax.add_annotation(base_span, **annotations)
                words.add_annotation(base_span)
                added = False
                start += len(form) + 1

            elif line == '\n' and not added:
                try:
                    sentences.add_annotation(words)
                    text.add_layer(words)
                    text.add_layer(compound_tokens)
                    text.add_layer(sentences)
                    text.add_layer(syntax)
                    text.text = ' '.join(sentence)
                    text.meta = {'doc': doc_info, 'chunk': chunk}
                    sentence = []
                    texts.append(text)
                    added = True
                    start = 0
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

                    syntax = Layer(name=layer_name, attributes=normal_attributes, text_object=text)
                    compound_tokens = Layer(name='compound_tokens', attributes=['type', 'normalized'], text_object=text)
                except:
                    print('Couldn\'t add layers to text: ' + text.text)
    if not added:
        text.meta = {'doc': doc_info, 'chunk': chunk}
        sentences.add_annotation(words)
        text.add_layer(words)
        text.add_layer(compound_tokens)
        text.add_layer(sentences)
        text.add_layer(syntax)
        text.text = ' '.join(sentence)
        texts.append(text)

    return texts
