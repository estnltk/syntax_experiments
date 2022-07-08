#from io import open
import sys
from tqdm.auto import tqdm
from .. reader import reader
from .. sentence import sentence

class Reader(reader.Reader):

    __FILE = None


    """
        Reading from custom file
    """
    def __init__(self, **kwargs):
        super().__init__()

        if 'file' in kwargs:
            self.__FILE  = kwargs['file']
        else:
            raise Exception("TSV filename is not set")

    def get_sentences_generator(self, mode='graph'):
        self.logInfo('Reading sentences in progress.')
        if mode not in ['graph', 'text']:
            raise Exception("Unknown mode %s", mode)
        word_id = 0
        count = 0
        current_sentence = []
        #
        G = sentence.Sentence()
        colId = None
        prevCol = 0
        global_sent_id = None
        total_lines = self.count_lines()
        with open(self.__FILE) as f:
            for line in tqdm(f, total=total_lines, desc='TSV lines'):
                unsaved = 1
                count +=1
                line = line.strip('\r\n')
                row = line.split('\t')
                if not len(row) == 9:
                    self.logError(line)
                    raise Exception(f'Wrong columns number line number {count} in TSV {self.__FILE}')
                data = {}
                prevCol = colId
                prev_global_sent_id = global_sent_id
                (colId, data['start'], data['id'], data['form'], data['lemma'], data['upostag'], data['deprel'], data['head'], data['feat']) = row
                colId = int(colId)
                for k in ('id', 'start', 'head'):
                    data[k] = int(data[k])
                #sentence start
                if data['id'] == 1:
                    if len(G.nodes):
                        current_sentence_text = ' '.join([s['form'] for s in current_sentence])
                        unsaved = 0
                        if mode == 'graph':
                            yield global_sent_id, G
                        else:
                            yield global_sent_id, current_sentence_text

                    current_sentence = []
                    G = sentence.Sentence()

                #paneme graafi kokku

                G.add_node(data['id'], id=data['id'], lemma=data['lemma'], pos=data['upostag'], deprel=data['deprel'], form=data['form'])
                G.add_edge(data['head'], data['id'], deprel = data['deprel'])

                current_sentence.append(data)

            #viimane lause
            if unsaved:
                current_sentence_text = ' '.join([s['form'] for s in current_sentence])
                if mode == 'graph':
                    yield global_sent_id, G
                else:
                    yield global_sent_id, current_sentence_text
            self.logInfo('Reading sentences done.')

    def count_lines(self):
        def blocks(files, size=65536):
            while True:
                b = files.read(size)
                if not b: break
                yield b

        with open(self.__FILE, "r",encoding="utf-8",errors='ignore') as f:
            return sum(bl.count("\n") for bl in blocks(f))
