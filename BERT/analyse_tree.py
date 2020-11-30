from estnltk.taggers import ConllMorphTagger, MaltParserTagger
from conllu import TokenList
import random
from estnltk.converters.conll_importer import conll_to_texts_list
from estnltk.taggers import WhiteSpaceTokensTagger
from estnltk import Text
import sys


## checks if tree changed using maltparser

def maltanalyse(texts):
    conll = ConllMorphTagger()
    malt = MaltParserTagger()
    tokenizer = WhiteSpaceTokensTagger(output_layer='words')
    neg = []
    pos = []
    i = 0
    for sent in texts.sentences:
        text = ' '.join(sent.text)
        t = Text(text)
        tokenizer.tag(t)
        t.analyse('all')
        conll.tag(t)
        malt.tag(t)
        negative = False
        sentence = []
        for span in t.maltparser_syntax:
            #print(span.text)
            goldspan = texts.conll_syntax[i]
            i += 1
            sentence.append('\t'.join(
                [str(goldspan.id), goldspan.text, goldspan.lemma, goldspan.upostag, goldspan.xpostag,
                 '|'.join(goldspan.feats.keys()) if goldspan.feats != None else '_', goldspan.deprel,
                 str(goldspan.head) + ' | ' + str(span.head), goldspan.deps if goldspan.deps != None else '_',
                 ''.join(goldspan.misc.keys()) if goldspan.misc != None else '_']))
            goldhead = str(goldspan.head)
            modelhead = str(span.head)
            if goldhead != modelhead:
                negative = True

        if not negative:
            pos.append(sentence)
        else:
            neg.append(sentence)

    possample = random.sample(pos, 100)
    for t in possample:
        with open('correct_100.conllu', 'w', encoding='utf-8') as f:
            for line in t:
                f.write(line + '\n')
            f.write('\n')

    negsample = random.rample(neg, 100)
    for t in negsample:
        with open('incorrect_100.conllu', 'w', encoding='utf-8') as f:
            for line in t:
                f.write(line + '\n')
            f.write('\n')


if __name__ == '__main__':
    file_name = sys.argv[1]
    texts = conll_to_texts_list(file_name)[0]
    maltanalyse(texts)
