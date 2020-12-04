from estnltk import Text
from estnltk.converters.conll_importer import conll_to_texts_list
from estnltk.taggers import WhiteSpaceTokensTagger
from collections import defaultdict
import sys
import matplotlib.pyplot as plt
from estnltk.vabamorf.morf import synthesize


def filter_dataset(newfile, out_file, texts):
    text = texts[0]
    tokenizer = WhiteSpaceTokensTagger(output_layer='words')
    f = open(newfile, 'w', encoding='utf-8')
    g = open(out_file, 'w', encoding='utf-8')
    i = 0
    count_all = len(text.sentences)
    count_suitable = 0
    mixed_xpos = defaultdict(lambda: defaultdict(int))
    can_add_all, all_correct_texts = [], []
    for sent in text.sentences:

        col = []
        for q in range(len(sent.text)):  # getting conll_syntax for one sentence
            col.append(text.conll_syntax[q + i])

        all_texts, words, input_words, all_correct_texts = [], [], [], []
        input_index = 0
        cor_word = None
        for p, span in enumerate(col):  # collecting all predicted words
            if span.deps == 'CHANGED':
                input_words = span.text.split('|')  # 10 bert predicted words
                input_index = p
                cor_word = ''.join(span.misc.keys())  # original word
            else:
                words.append(span.text)
        for word in input_words:  # creating raw text, augmented ones and original
            all_correct_texts.append(' '.join(words[0:input_index] + [cor_word] + words[input_index:]))  # from original
            all_texts.append(' '.join(words[0:input_index] + [word] + words[input_index:]))  # new augmented texts

        outoften = 0

        for raw_text, cor_raw in zip(all_texts, all_correct_texts):
            track = i
            tcor = Text(cor_raw)  # original sentence
            tokenizer.tag(tcor)
            tcor.analyse('morphology')

            t = Text(raw_text)  # new augmented word
            tokenizer.tag(t)
            t.analyse('morphology')

            can_add = False
            new_sentence = []

            for morph_an, tcorrect in zip(t.morph_analysis, tcor.morph_analysis):
                gold = text.conll_syntax[track]
                if gold.deps == 'CHANGED':
                    a_pos = morph_an.partofspeech[0]
                    gold_upos, gold_xpos, gold_form, bert_form = gold.upostag, gold.xpostag, ''.join(
                        gold.misc.keys()), morph_an.text
                    if a_pos == gold_xpos and gold_form != bert_form:
                        can_add = True

                        outoften += 1

                    if tcorrect.form[0] != '':

                        newform = synthesize(morph_an.lemma[0], tcorrect.form[0])
                        if newform == []:
                            can_add = False
                            newform = morph_an.text
                            count_suitable += 1
                        else:
                            newform = newform[0]
                    else:
                        newform = morph_an.lemma[0]
                    feats = str('|'.join(gold.feats.keys())) if gold.feats != None else '_'
                    tostr = '\t'.join(
                        [str(gold.id), newform, morph_an.lemma[0], str(gold.upostag), str(gold.xpostag), feats,
                         str(gold.head), str(gold.deprel), 'CHANGED', ''.join(gold.misc.keys())]) + '\n'
                    new_sentence.append(tostr)
                else:
                    a_pos, gold_xpos = morph_an.partofspeech[0], gold.xpostag
                    mixed_xpos[gold_xpos][a_pos] += 1
                    feats = str('|'.join(gold.feats.keys())) if gold.feats != None else '_'
                    tostr = '\t'.join(
                        [str(gold.id), str(gold.text), str(gold.lemma), str(gold.upostag), str(gold.xpostag), feats,
                         str(gold.head), str(gold.deprel), '_', '_']) + '\n'
                    new_sentence.append(tostr)
                track += 1
            if can_add:
                for s in new_sentence:
                    f.write(s)
                f.write('\n')
                new_sentence = []
            else:
                for s in new_sentence:
                    g.write(s)
                g.write('\n')
        can_add_all.append(outoften)
        i += len(sent.words)
    g.close()
    f.close()
    return count_all, count_suitable, mixed_xpos, can_add_all


if __name__ == '__main__':
    i = sys.argv[1]
    texts = conll_to_texts_list('new_data/train_' + i + '_mod_newest_512_10.conllu')
    count_all, count_suitable, mixed_xpos, can_add_all = filter_dataset('train_data/train_' + i + '.conllu',
                                                                        'train_neg/train_' + i + '.conllu',
                                                                        texts)
    with open('train_data/stat_' + i + '.txt', 'w', encoding='utf-8') as f:
        f.write('count all: ' + str(count_all) + '\n')
        f.write('count suitable ' + str(count_suitable) + '\n')

        f.write('real_xpos new_xpos count\n')
        for k1 in mixed_xpos.keys():
            for k2 in mixed_xpos.get(k1).keys():
                val = mixed_xpos.get(k1).get(k2)
                f.write(k1 + ' ' + k2 + ' ' + str(val) + '\n')
            f.write('\n')
    plt.hist(can_add_all, bins=10)
    plt.xlabel('Possible sentence count per one orig sentence')
    plt.ylabel('Count')
    plt.savefig('train_data/hist_' + i + '.png')
