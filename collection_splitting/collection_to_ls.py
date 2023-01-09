from estnltk import Text
import random
import json
from typing import List


def conf_gen(classes: List[str]):
    single_label = '\t<Label value="{label_value}" background="{background_value}"/> \n'
    conf_string = """
<View>
    <Labels name="label" toName="text">\n"""
    end_block = """
    </Labels>
<Text name="text" value="$text"/>
<Header value="Is the entity free, bound, incorrect or causes unnatural sentence?"/>
<Choices name="review" toName="text">
    <Choice value="free"/>
    <Choice value="bound"/>
    <Choice value="unnatural"/>
    <Choice value="not correct entity"/>
</Choices>
</View>"""

    for entry in classes:
        conf_string += single_label.format(
            label_value=entry,
            background_value=("#" + "%06x" % random.randint(0, 0xFFFFFF)).upper()
        )
    conf_string += end_block

    return conf_string


def one_text(text: Text, regular_layers: List[str], classification_layer: str = None, ner_layer: str = None):
    predictions = []
    results = {}
    score = None

    if classification_layer:
        if len(text[classification_layer]) > 0:
            print("üks")
            span = text[classification_layer][0]

            label = text[classification_layer][0]['label']
            score = text[classification_layer][0]['score']

            # Ignore spans without labels
            predictions.append({
                'to_name': "text",
                'from_name': "label",
                'type': 'labels',
                'value': {
                    "start": span.start,
                    "end": span.end,
                    "score": float(score),
                    "text": span.text,
                    "labels": [
                        str(classification_layer + "_" + label)
                    ]
                }
            })

    for_sure_piir = 0.75
    uncertain_piir = 0.25

    if ner_layer:
        if len(text[ner_layer]) > 0:
            for span in text[ner_layer]:
                score = span['score']

                suffix = None
                if score >= for_sure_piir:
                    suffix = "_" + str(for_sure_piir)
                elif uncertain_piir <= score < for_sure_piir:
                    suffix = "_" + str(uncertain_piir)
                if suffix:
                    predictions.append({

                        'to_name': "text",
                        'from_name': "label",
                        'type': 'labels',
                        'value': {
                            "start": span.start,
                            "end": span.end,
                            "score": float(score),
                            "text": span.text,
                            "labels": [
                                str(ner_layer + suffix)
                            ]
                        }
                    })

    for layer in regular_layers:
        if len(text[layer]) == 1:
            span = text[layer][0]
            predictions.append({

                'to_name': "text",
                'from_name': "label",
                'type': 'labels',
                'value': {
                    "start": span.start,
                    "end": span.end,
                    "text": span.text,
                    "labels": [
                        str(layer)
                    ]
                }
            })
            results = {
                'data': {'text': text.text},
                'predictions': [{
                    'result': predictions}]
            }

        elif len(text[layer]) > 1:
            results = []
            for i, span in enumerate(text[layer]):
                predictions = [{
                    'to_name': "text",
                    'from_name': "label",
                    'type': 'labels',
                    'value': {
                        "start": span.start,
                        "end": span.end,
                        "text": span.text,
                        "labels": [
                            str(layer)
                        ]
                    }
                }]
                results.append({
                    'data': {'text': text.text},
                    'predictions': [{
                        'result': predictions}]
                })

    # if score and classification_layer:
    #    results['predictions'][0]['score'] = float(score)

    return results


def collection_to_labelstudio(collection,
                              regular_layers: List[str], filename: str,
                              classification_layer: str = None,
                              ner_layer: str = None
                              ):

    # Make sure imported layers exist in collection
    # assert something

    texts_list = [text for text in collection]

    data1 = [one_text(
        text,
        classification_layer=classification_layer,
        ner_layer=ner_layer,
        regular_layers=regular_layers) for text in texts_list]
    data = []
    for elem in data1:
        if type(elem) == list:
            for e in elem:
                data.append(e)
        else:
            data.append(elem)

    with open(filename, 'w') as f:
        json.dump(data, f)
