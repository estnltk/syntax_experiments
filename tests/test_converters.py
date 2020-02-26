from converters.conll_to_conllu_format import conll_to_conllu_text_list
from converters.conllu_importer import conllu_file_to_texts_list


def test_conllu_importer():
    test_file = 'test.conllu'
    texts = conllu_file_to_texts_list(test_file)
    assert len(texts) == 3
    assert 'syntax_gold' in texts[0].layers
    assert 'words' in texts[0].layers
    assert 'sentences' in texts[0].layers
    assert texts[0].text == 'Keskpanga avalike suhete osakonna juht Andrus Kuusmann ütleb , et " kui tegu olnuks tõestatud rahapesuga , siis oleks ka vastavalt reageeritud " .'

def test_conll_to_conllu_to_text_list():
    test_file = 'test_conll.conll'
    texts = conll_to_conllu_text_list(test_file)
    assert len(texts) == 3
    assert 'syntax_gold' in texts[0].layers
    assert 'words' in texts[0].layers
    assert 'sentences' in texts[0].layers

