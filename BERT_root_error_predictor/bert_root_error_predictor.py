from transformers import BertTokenizer, BertForSequenceClassification
import torch
import numpy as np


class BertSyntaxRootErrorPredictor():
    def __init__(self, model_location: str):
        self.tokenizer = BertTokenizer.from_pretrained(model_location)
        self.model = BertForSequenceClassification.from_pretrained(model_location, return_dict=True)


    def predict(self, sentence: str) -> int:
        inputs = self.tokenizer(sentence, return_tensors="pt")
        labels = torch.tensor([1]).unsqueeze(0)
        outputs = self.model(**inputs, labels=labels)
        logits = outputs.logits
        preds = logits.detach().cpu().numpy()
        prediction = np.argmax(preds, axis=1)

        return prediction[0]


