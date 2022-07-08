
from io import open
from conllu import parse
import os
from tqdm.auto import tqdm

from .. reader import reader
from .. sentence import sentence


class Reader(reader.Reader):
    __CONLLU_ROOT = './'
    __connlu_files = []

    """
        path = path of conllu files
    """
    def __init__(self,  **kwargs):
        super().__init__()
        if 'path' in kwargs:
            self.__CONLLU_ROOT  = kwargs['path']

    def getFilesList(self):
        self.__connlu_files = []
        for path, subdirs, files in os.walk(self.__CONLLU_ROOT):
            for name in files:
                if name.endswith('.conllu'):
                    self.__connlu_files.append((path.replace(self.__CONLLU_ROOT, ''), name))
        self.__connlu_files = sorted(self.__connlu_files)

    def get_sentences_generator(self, mode='graph'):
        if mode not in ['graph', 'text']:
            raise Exception("Unknown mode %s", mode)

        word_id = 0
        # alustame kaustade rekursiivset läbimist
        self.getFilesList()

        for directory, file  in tqdm(self.__connlu_files, 'Conllu files'):
            fullpath = f"{self.__CONLLU_ROOT}{directory}/{file}"
            filepath = f"{directory}/{file}"
            data_file = open(f"{fullpath}", "r", encoding="utf-8")
            data = data_file.read()
            sentences_counter = 0
            try:
                sentences = parse(data)
                #self.logInfo(f'Parsed OK {fullpath}')
            except:
                self.logError(f'Conllu parser error parsing {fullpath}')
                continue
            for sent in sentences:
                sentences_counter +=1
                if not 'metadata' in sent:
                    originaltext = ' '.join( [data['form'] for data in sent])
                    sent_id = sentences_counter
                else:
                    originaltext = sent.metadata['text']
                    sent_id = sent.metadata['sent_id']

                global_sent_id = f'{directory}/{file}_{sent_id}'
                G = sentence.Sentence.make_graph_conllu(sent)
                if mode == 'graph':
                    yield global_sent_id, G
                else:
                    yield global_sent_id, originaltext
