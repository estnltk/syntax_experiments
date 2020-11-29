import random
import torch
from transformers import AutoTokenizer, AutoModel, AutoModelWithLMHead
import logging

logging.basicConfig(level=logging.INFO)
from copy import deepcopy
from collections import defaultdict
import sys


def predict_10_mask(sentence, model, tokenizer):
    seq = deepcopy(sentence)
    mask1 = random.choice([i for i in range(len(sentence))])
    seq[mask1] = '[MASK]'
    sequence = ' '.join(seq)
    input = tokenizer.encode(sequence, return_tensors="pt")
    mask_token_index = torch.where(input == tokenizer.mask_token_id)[1]

    token_logits = model(input).logits
    mask_token_logits = token_logits[0, mask_token_index, :]
    top_10_tokens = torch.topk(mask_token_logits, 10, dim=1).indices[0].tolist()
    tokens = []
    for token in top_10_tokens:
        tokens.append(tokenizer.decode([token]))

    return tokens, mask1


if __name__ == '__main__':
    fold = sys.argv[1]
    pretrained_model = 'tartuNLP/EstBERT_512'
    tokenizer = AutoTokenizer.from_pretrained(pretrained_model)
    model = AutoModelWithLMHead.from_pretrained(pretrained_model, return_dict=True)
    g = open('new_data/train_' + fold + '_512_10.conllu', 'w', encoding='utf-8')
    changed = defaultdict(int)
    with open('data/train_' + fold + '.conllu', 'r', encoding='utf-8') as f:
        sentence, lines, col_tok = [], [], []
        for line in f:
            if line != '\n':
                line = line.strip().split('\t')
                sentence.append(line[1])
                lines.append(line)
            else:
                tokens, j = predict_10_mask(sentence, model, tokenizer)
                if tokens == None:
                    continue
                i = 0
                try:
                    for word, line in zip(sentence, lines):
                        if i == j:
                            line[8] = 'CHANGED'
                            line[9] = word
                            word = '|'.join(tokens)
                        i += 1
                        line[1] = word
                        g.write('\t'.join(line) + '\n')
                        col_tok = []
                    sentence, lines = [], []
                    g.write('\n')

                except Exception as e:
                    print(e)

    g.close()
