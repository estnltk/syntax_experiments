from converters.conllu_importer import conllu_file_to_texts_list
from experiment_taggers.experiment_1.am_experiment_1_tagger import AMExperiment1Tagger
from experiment_taggers.experiment_1.gm_experiment_1_tagger import GMExperiment1Tagger
from experiment_taggers.experiment_10.gm_experiment_10_tagger import GMExperiment10Tagger
from experiment_taggers.experiment_11.gm_experiment_11_tagger import GMExperiment11Tagger
from experiment_taggers.experiment_12.gm_experiment_12_tagger import GMExperiment12Tagger
from experiment_taggers.experiment_13.gm_experiment_13_tagger import GMExperiment13Tagger
from experiment_taggers.experiment_14.gm_experiment_14_tagger import GMExperiment14Tagger
from experiment_taggers.experiment_2.am_experiment_2_tagger import AMExperiment2Tagger
from experiment_taggers.experiment_2.gm_experiment_2_tagger import GMExperiment2Tagger
from experiment_taggers.experiment_3.gm_experiment_3_tagger import GMExperiment3Tagger
from experiment_taggers.experiment_3_2.gm_experiment_3_2_tagger import GMExperiment3_2Tagger
from experiment_taggers.experiment_4.gm_experiment_4_tagger import GMExperiment4Tagger
from experiment_taggers.experiment_4_2.gm_experiment_4_2_tagger import GMExperiment4_2Tagger
from experiment_taggers.experiment_5.gm_experiment_5_tagger import GMExperiment5Tagger
from experiment_taggers.experiment_6.gm_experiment_6_tagger import GMExperiment6Tagger
from experiment_taggers.experiment_6_2.gm_experiment_6_2_tagger import GMExperiment6_2Tagger
from experiment_taggers.experiment_7.gm_experiment_7_tagger import GMExperiment7Tagger
from experiment_taggers.experiment_7_2.gm_experiment_7_2_tagger import GMExperiment7_2Tagger
from experiment_taggers.experiment_8.gm_experiment_8_tagger import GMExperiment8Tagger
from experiment_taggers.experiment_8_2.gm_experiment_8_2_tagger import GMExperiment8_2Tagger
from experiment_taggers.experiment_9.gm_experiment_9_tagger import GMExperiment9Tagger


conll_texts_for_testing = conllu_file_to_texts_list("test_taggers.conll")
to_tag_text = conllu_file_to_texts_list("test_text.conll")[0]

def test_gm_experiment_1():
    test_file = 'test.conllu'
    text = conllu_file_to_texts_list(test_file)[0]
    ex1 = GMExperiment1Tagger()
    ex1.tag(text)
    assert 'gm_experiment_1' in text.layers
    assert text.gm_experiment_1.attributes == text.syntax_gold.attributes
    for t_span, g_span in zip(text.gm_experiment_1, text.syntax_gold):
        for attribute in text.gm_experiment_1.attributes:
            assert t_span[attribute] == g_span[attribute]


def test_am_experiment_1():
    test_file = 'test.conllu'
    text = conllu_file_to_texts_list(test_file)[0]

    ex1 = AMExperiment1Tagger()
    ex1.tag(text)

    feats = ['com|sg|gen', 'pos|pl|gen', 'com|pl|gen', 'com|sg|gen', 'com|sg|nom', 'prop|sg|nom', 'prop|sg|nom',
             'main|indic|pres|ps|ps3|sg|af', 'Com', 'sub', 'Quo', 'sub', 'com|sg|nom', 'main|cond|past|ps|af',
             'main|past|imps', 'com|sg|kom', 'Com', '_', 'aux|cond|pres|ps|af', '_', 'post', 'main|past|imps',
             'Quo', 'Fst']

    assert 'am_experiment_1' in text.layers
    assert text.am_experiment_1.attributes == text.syntax_gold.attributes
    for t_span, g_span, feat in zip(text.am_experiment_1, text.syntax_gold, feats):
        for attribute in text.am_experiment_1.attributes:
            if attribute == 'feats':
                assert t_span[attribute] == feat
            else:
                assert t_span[attribute] == g_span[attribute]


def test_gm_experiment_2():
    test_file = 'test.conllu'
    text = conllu_file_to_texts_list(test_file)[0]
    ex2 = GMExperiment2Tagger()
    ex2.tag(text)
    assert 'gm_experiment_2' in text.layers
    assert text.gm_experiment_2.attributes == text.syntax_gold.attributes
    for t_span, g_span in zip(text.gm_experiment_2, text.syntax_gold):
        for attribute in text.gm_experiment_2.attributes:
            if attribute == 'lemma':
                assert t_span.lemma == 'XX'
            else:
                assert t_span[attribute] == g_span[attribute]


def test_am_experiment_2():
    test_file = 'test.conllu'
    text = conllu_file_to_texts_list(test_file)[0]
    ex2 = AMExperiment2Tagger()
    ex2.tag(text)
    assert 'am_experiment_2' in text.layers
    assert text.am_experiment_2.attributes == text.syntax_gold.attributes
    for t_span, g_span in zip(text.am_experiment_2, text.syntax_gold):
        for attribute in text.am_experiment_2.attributes:
            if attribute == 'feats':
                pass
            elif attribute == 'lemma':
                assert t_span.lemma == 'XX'
            else:
                assert t_span[attribute] == g_span[attribute]


def test_gm_experiment_3():
    test_file = 'test.conllu'
    text = conllu_file_to_texts_list(test_file)[0]
    ex2 = GMExperiment3Tagger()
    ex2.tag(text)
    assert 'gm_experiment_3' in text.layers
    assert text.gm_experiment_3.attributes == text.syntax_gold.attributes
    for t_span, g_span in zip(text.gm_experiment_3, text.syntax_gold):
        for attribute in text.gm_experiment_3.attributes:
            if attribute == 'feats':
                pass
            if attribute == 'lemma' and g_span.syntax_gold.upostag in ('S', 'A'):
                assert t_span.lemma == 'XX'
            else:
                assert t_span[attribute] == g_span[attribute]


def test_gm_experiment_2_alt():
    test_layer = conll_texts_for_testing[0]

    ex2 = GMExperiment2Tagger()
    ex2.tag(to_tag_text)
    assert 'gm_experiment_2' in to_tag_text.layers

    for right_span, tagged_span in zip(test_layer.syntax_gold, to_tag_text.gm_experiment_2):
        assert right_span == tagged_span

def test_gm_experiment_3_alt():
    test_layer = conll_texts_for_testing[1]

    ex3 = GMExperiment3Tagger()
    ex3.tag(to_tag_text)
    assert 'gm_experiment_3' in to_tag_text.layers

    for right_span, tagged_span in zip(test_layer.syntax_gold, to_tag_text.gm_experiment_3):
        for attr in to_tag_text.syntax_gold.attributes:
            assert right_span[attr] == tagged_span[attr]


def test_gm_experiment_3_2():

    test_layer = conll_texts_for_testing[2]


    ex3_2 = GMExperiment3_2Tagger()
    ex3_2.tag(to_tag_text)
    assert 'gm_experiment_3_2' in to_tag_text.layers

    for right_span, tagged_span in zip(test_layer.syntax_gold, to_tag_text.gm_experiment_3_2):
        for attr in to_tag_text.gm_experiment_3_2.attributes:

            assert right_span[attr] == tagged_span[attr]


def test_gm_experiment_4():
    test_layer = conll_texts_for_testing[3]

    ex4 = GMExperiment4Tagger()
    ex4.tag(to_tag_text)
    assert 'gm_experiment_4' in to_tag_text.layers

    for right_span, tagged_span in zip(test_layer.syntax_gold, to_tag_text.gm_experiment_4):

        for attr in to_tag_text.syntax_gold.attributes:

            assert right_span[attr] == tagged_span[attr]


def test_gm_experiment_4_2():
    test_layer = conll_texts_for_testing[4]

    ex4_2 = GMExperiment4_2Tagger()
    ex4_2.tag(to_tag_text)
    assert 'gm_experiment_4_2' in to_tag_text.layers

    for right_span, tagged_span in zip(test_layer.syntax_gold, to_tag_text.gm_experiment_4_2):
        for attr in to_tag_text.syntax_gold.attributes:
            print(tagged_span[attr])
            assert right_span[attr] == tagged_span[attr]



def test_gm_experiment_5():
    test_layer = conll_texts_for_testing[5]

    ex5 = GMExperiment5Tagger()
    ex5.tag(to_tag_text)
    assert 'gm_experiment_5' in to_tag_text.layers

    for right_span, tagged_span in zip(test_layer.syntax_gold, to_tag_text.gm_experiment_5):
        assert right_span == tagged_span

def test_gm_experiment_6():
    test_layer = conll_texts_for_testing[6]

    ex6 = GMExperiment6Tagger()
    ex6.tag(to_tag_text)
    assert 'gm_experiment_6' in to_tag_text.layers

    for right_span, tagged_span in zip(test_layer.syntax_gold, to_tag_text.gm_experiment_6):
        assert right_span == tagged_span

def test_gm_experiment_6_2():
    test_layer = conll_texts_for_testing[7]

    ex6_2 = GMExperiment6_2Tagger()
    ex6_2.tag(to_tag_text)
    assert 'gm_experiment_6_2' in to_tag_text.layers

    for right_span, tagged_span in zip(test_layer.syntax_gold, to_tag_text.gm_experiment_6_2):
        for attr in to_tag_text.syntax_gold.attributes:
            print(tagged_span[attr])
            assert right_span[attr] == tagged_span[attr]

def test_gm_experiment_7():
    test_layer = conll_texts_for_testing[8]

    ex7 = GMExperiment7Tagger()
    ex7.tag(to_tag_text)
    assert 'gm_experiment_7' in to_tag_text.layers

    for right_span, tagged_span in zip(test_layer.syntax_gold, to_tag_text.gm_experiment_7):
        for attr in to_tag_text.syntax_gold.attributes:
            print(tagged_span[attr])
            assert right_span[attr] == tagged_span[attr]

def test_gm_experiment_7_2():
    test_layer = conll_texts_for_testing[9]

    ex7_2 = GMExperiment7_2Tagger()
    ex7_2.tag(to_tag_text)
    assert 'gm_experiment_7_2' in to_tag_text.layers

    for right_span, tagged_span in zip(test_layer.syntax_gold, to_tag_text.gm_experiment_7_2):
        for attr in to_tag_text.syntax_gold.attributes:
            print(tagged_span[attr])
            assert right_span[attr] == tagged_span[attr]

def test_gm_experiment_8():
    test_layer = conll_texts_for_testing[10]

    ex8 = GMExperiment8Tagger()
    ex8.tag(to_tag_text)
    assert 'gm_experiment_8' in to_tag_text.layers

    for right_span, tagged_span in zip(test_layer.syntax_gold, to_tag_text.gm_experiment_8):
        for attr in to_tag_text.syntax_gold.attributes:
            print(tagged_span[attr])
            assert right_span[attr] == tagged_span[attr]

def test_gm_experiment_8_2():
    test_layer = conll_texts_for_testing[11]

    ex8_2 = GMExperiment8_2Tagger()
    ex8_2.tag(to_tag_text)
    assert 'gm_experiment_8_2' in to_tag_text.layers

    for right_span, tagged_span in zip(test_layer.syntax_gold, to_tag_text.gm_experiment_8_2):
        for attr in to_tag_text.syntax_gold.attributes:
            print(tagged_span[attr])
            assert right_span[attr] == tagged_span[attr]

def test_gm_experiment_9():
    test_layer = conll_texts_for_testing[12]

    ex9 = GMExperiment9Tagger()
    ex9.tag(to_tag_text)
    assert 'gm_experiment_9' in to_tag_text.layers

    for right_span, tagged_span in zip(test_layer.syntax_gold, to_tag_text.gm_experiment_9):
        for attr in to_tag_text.syntax_gold.attributes:
            print(tagged_span[attr])
            assert right_span[attr] == tagged_span[attr]

def test_gm_experiment_10():
    test_layer = conll_texts_for_testing[13]

    ex10 = GMExperiment10Tagger()
    ex10.tag(to_tag_text)
    assert 'gm_experiment_10' in to_tag_text.layers

    for right_span, tagged_span in zip(test_layer.syntax_gold, to_tag_text.gm_experiment_10):
        assert right_span == tagged_span

def test_gm_experiment_11():
    test_layer = conll_texts_for_testing[14]

    ex11 = GMExperiment11Tagger()
    ex11.tag(to_tag_text)
    assert 'gm_experiment_11' in to_tag_text.layers

    for right_span, tagged_span in zip(test_layer.syntax_gold, to_tag_text.gm_experiment_11):
        for attr in to_tag_text.syntax_gold.attributes:
            print(tagged_span[attr])
            assert right_span[attr] == tagged_span[attr]

def test_gm_experiment_12():
    test_layer = conll_texts_for_testing[15]

    ex12 = GMExperiment12Tagger()
    ex12.tag(to_tag_text)
    assert 'gm_experiment_12' in to_tag_text.layers

    for right_span, tagged_span in zip(test_layer.syntax_gold, to_tag_text.gm_experiment_12):
        for attr in to_tag_text.syntax_gold.attributes:
            print(tagged_span[attr])
            assert right_span[attr] == tagged_span[attr]


