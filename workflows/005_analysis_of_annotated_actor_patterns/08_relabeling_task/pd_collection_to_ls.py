from estnltk import Text
import random
import json
from typing import List
from tqdm import tqdm 

def conf_gen(classes: List[str]):
    #single_label = '\t<Label value="{label_value}" background="{background_value}"/> \n'
    conf_string = """
<View>
    <Labels name="label" toName="text">\n
	<Label value="V" background="#7AC130"/> 
    <Label value="OBL" background="#0795E2"/> 
    """
    # <Label value="COMP" background="#7AC130"/> 
    #<Label value="OBLP" background="#EA5664"/> 

    end_block = """
</Labels>
<Text name="text" value="$text"/>
<Header value="Kas tegu on aja- või kohamäärusega?"/>
<Choices name="aegkoht" toName="text">
    <Choice value="alati"/>
    <Choice value="vahel"/>
    <Choice value="mitte kunagi"/>
  </Choices>
<Header value="Kas tegu on isiku või organisatsiooniga?"/>
<Choices name="per_org" toName="text">
    <Choice value="alati"/>
    <Choice value="vahel"/>
    <Choice value="mitte kunagi"/>
  </Choices>
<Header value="Kas tegu on millegi muuga?"/>
<Choices name="muu" toName="text">
    <Choice value="muu"/>
  <Choice value="pole kindel"/>
</Choices>
</View>"""

    """for entry in classes:
        conf_string += single_label.format(
            label_value=entry,
            background_value=("#" + "%06x" % random.randint(0, 0xFFFFFF)).upper()
        )"""
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
            data = {'text': text.text} 
            results = {
                'data': data,
                'predictions': [{
                    'result': predictions}
                    ]
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
                data = {'text': text.text} 
                results.append({
                    'data': data,
                    'predictions': [{
                        'result': predictions}
                        ]
                })
                

    # if score and classification_layer:
    #    results['predictions'][0]['score'] = float(score)

    return results


def from_pd_dataframe_single(row):
    predictions = []
    results = {}
    
    # verb
    predictions.append({

            'to_name': "text",
            'from_name': "label",
            'type': 'labels',
            'value': {
                "start": int(row["verb_start"]),  # span.start,
                "end": int(row["verb_end"]) , # span.end,
                "text":  str(row["verb_text"])   ,   #span.text,
                "labels": [
                    str(row["verb_label"])
                ]
            }
        
            })
    # verb compound       
    if row["verb_comp_spans"] is not None:
        spans = json.loads(row["verb_comp_spans"])
        for span in spans:
            predictions.append({

                    'to_name': "text",
                    'from_name': "label",
                    'type': 'labels',
                    'value': {
                        "start": int(span["start"]),  # span.start,
                        "end": int(span["end"]) , # span.end,
                        "text":  str(span["text"])   ,   #span.text,
                        "labels": [
                            str(span["labels"][0])
                        ]
                    }
                
                    })
            
     # obl
    predictions.append({

            'to_name': "text",
            'from_name': "label",
            'type': 'labels',
            'value': {
                "start": int(row["obl_start"]),  # span.start,
                "end": int(row["obl_end"]) , # span.end,
                "text":  str(row["obl_text"])   ,   #span.text,
                "labels": [
                    str(row["obl_label"])
                ]
            }
        
            })       
    
    # obl compound       
    if row["oblp"] is not None:
        spans = json.loads(row["oblp"])
        for span in spans:
            predictions.append({

                    'to_name': "text",
                    'from_name': "label",
                    'type': 'labels',
                    'value': {
                        "start": int(span["start"]),  # span.start,
                        "end": int(span["end"]) , # span.end,
                        "text":  str(span["text"])   ,   #span.text,
                        "labels": [
                            str(span["labels"][0])
                        ]
                    }
                
                    })   
            
            
            
    data = {'text': str(row["sentence"])} 
    results = {
        'data': data,
        'predictions': [{
            'result': predictions}
            ]
    }
        
    #results.append(result)
        
        
    #print(len(results) )
    #print(results[0])
    return results



def from_pd_dataframe(row):
    predictions = []
    results = {}
    
    # verb
    for i in range(len(row["verb_form"])):
        predictions.append({
                
                'to_name': "text",
                'from_name': "label",
                'type': 'labels',
                'value': {
                    "start": int(row["new_verb_span"][i][0]),  # span.start,
                    "end": int(row["new_verb_span"][i][1]) , # span.end,
                    "text":  str(row["verb_form"][i])   ,   #span.text,
                    "labels": [
                        str("V")
                    ]
                }
            
                })
    # verb compound       
    """spans = row["verb_comp_spans"]
    for span1 in spans:
        if str(span1) != "None":
            #print(span1, str(span1)=="None", span1==None)
            if type(span1)==str:
                span2 = json.loads(span1)
            else:
                span2 = span1
            for span in span2:
                predictions.append({

                        'to_name': "text",
                        'from_name': "label",
                        'type': 'labels',
                        'value': {
                            "start": int(span["start"]),  # span.start,
                            "end": int(span["end"]) , # span.end,
                            "text":  str(span["text"])   ,   #span.text,
                            "labels": [
                                str(span["labels"][0])
                            ]
                        }
                    
                        })
    """        
    # obl
    for i in range(len(row["root_form"])):
        predictions.append({

                'to_name': "text",
                'from_name': "label",
                'type': 'labels',
                'value': {
                    "start": int(row["new_root_span"][i][0]),  # span.start,
                    "end": int(row["new_root_span"][i][1]) , # span.end,
                    "text":  str(row["root_form"][i])   ,   #span.text,
                    "labels": [
                        str("OBL")
                    ]
                }
            
                })       
    """
    # obl compound       
    spans = row["oblp"]
    #print("oblp spans", spans)
    for span1 in spans:
        if str(span1) !="None":
            #print(span1, span1=="None", span1==None)
            if type(span1)==str:
                span2 = json.loads(span1)
            else:
                span2 = span1
            for span in span2:
                #print(span)
                predictions.append({

                        'to_name': "text",
                        'from_name': "label",
                        'type': 'labels',
                        'value': {
                            "start": int(span["start"]),  # span.start,
                            "end": int(span["end"]) , # span.end,
                            "text":  str(span["text"])   ,   #span.text,
                            "labels": [
                                str(span["labels"][0])
                            ]
                        }
                    
                        })   
    """        
    data = {'text': str(row["ilus_osa_enne"]) + str("\n".join(row["sentence"]))} 
    results = {
        'data': data,
        'predictions': [{
            'result': predictions}
            ]
    }
        
    #results.append(result)
        
        
    #print(len(results) )
    #print(results[0])
    return results



def collection_to_labelstudio(collection, 
                                #deprel, 
                               
                               filename: str,
                               state: str, # single or multi
                               regular_layers: List[str]=None,
                              classification_layer: str = None,
                              ner_layer: str = None
                              ):

    if state == "single":
        data1 = [from_pd_dataframe_single(collection.iloc[i]) for i in range(len(collection))]
    elif state == "multi":
        data1 = [from_pd_dataframe(collection.iloc[i]) for i in range(len(collection))]
    else:
        raise Valuerror("Please provide correct state!")
    data = []
    
    for elem in data1:
        if type(elem) == list:
            for e in elem:
                data.append(e)
        else:
            data.append(elem)
    #print(data)
    with open(filename, 'w') as f:
        json.dump(data, f)

