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
        #global line counter
        count = 0
        #current sentence data
        current_sentence = []
        # sentence graph object
        G = sentence.Sentence()
        # current collection id
        colId = None
        # prev collection id
        prevCol = 0
        #global sentence id - collid_sentensespanstart_sentencecountincollection
        global_sent_id = None
        #sentence counter in collection
        coll_sentence_counter = 0
        sentence_span_start = 0
        #total lines in TSV file for progressbar calculations
        total_lines = self.count_lines()

        with open(self.__FILE) as f:
            for line in tqdm(f, total=total_lines, desc='TSV lines'):
                unsaved = 1
                count +=1
                line = line.strip('\r\n')
                row = line.split('\t')
                if not len(row) == 10:
                    self.logError(line)
                    raise Exception(f'Wrong columns number line number {count} in TSV {self.__FILE}')
                data = {}
                if not prevCol == colId:
                    coll_sentence_counter = 0
                prevCol = colId
                prev_global_sent_id = global_sent_id
                prev_sentence_span_start = sentence_span_start
                (colId, data['start'], data['id'], data['form'], data['lemma'], data['upostag'], data['deprel'], data['head'], data['feat'], data['clause']) = row
                colId = int(colId)
                for k in ('id', 'start', 'head'):
                    data[k] = int(data[k])
                #sentence start
                if data['id'] == 1:
                    coll_sentence_counter += 1
                    sentence_span_start = data['start']
                    if len(G.nodes):
                        global_sent_id = '%i_%i_%i' % (prevCol, prev_sentence_span_start, coll_sentence_counter , )
                        current_sentence_text = ' '.join([s['form'] for s in current_sentence])
                        unsaved = 0
                        if mode == 'graph':
                            yield global_sent_id, G
                        else:
                            yield global_sent_id, current_sentence_text

                    current_sentence = []
                    G = sentence.Sentence()

                #paneme graafi kokku

                G.add_node(data['id'], id=data['id'], lemma=data['lemma'], pos=data['upostag'], deprel=data['deprel'], form=data['form'], clause=data['clause'])
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
