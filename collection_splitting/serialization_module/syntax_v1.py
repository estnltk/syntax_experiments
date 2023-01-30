from estnltk_core.converters.default_serialisation import dict_to_layer as default_dict_to_layer

from typing import Union

from estnltk_core.layer.base_layer import to_base_span
from estnltk_core.layer.layer import Layer

__version__ = 'syntax_v1'

def layer_to_dict(layer):
    layer_dict = {
        'name': layer.name,
        'attributes': layer.attributes,
        'secondary_attributes': layer.secondary_attributes,
        'parent': layer.parent,
        'enveloping': layer.enveloping,
        'ambiguous': layer.ambiguous,
        'serialisation_module': __version__,
        'meta': layer.meta
    }

    spans = []
    attributes = [attr for attr in layer.attributes if attr not in {'parent_span', 'children'}]
    for span in layer:
        annotation_dict = []
        for annotation in span.annotations:
            for attr in attributes:
                if attr == "root":
                    annotation_dict.append({"root_id": annotation[attr]['id'] })
                    annotation_dict.append({attr: None })
                else:
                    annotation_dict.append({attr: annotation[attr] })
        spans.append({'base_span': span.base_span.raw(),
                      'annotations': annotation_dict})
    layer_dict['spans'] = spans

    return layer_dict


def dict_to_layer(layer_dict: dict, text_object=None):
    layer = Layer(name=layer_dict['name'],
                  attributes=layer_dict['attributes'],
                  secondary_attributes=layer_dict.get('secondary_attributes', ()),
                  text_object=text_object,
                  parent=layer_dict['parent'],
                  enveloping=layer_dict['enveloping'],
                  ambiguous=layer_dict['ambiguous'],
                  )
    layer.meta.update(layer_dict['meta'])
    
    for span_dict in layer_dict['spans']:
        base_span = to_base_span(span_dict['base_span'])
        for annotation in span_dict['annotations']:
            if list(annotation.keys())[0]=="root_id":
                root_id = annotation[list(annotation.keys())[0]]
            elif list(annotation.keys())[0]=="root":
                span =  text_object["stanza_syntax"].spans[root_id-1]
                root_id = None 
                layer.add_annotation(base_span, **{"root":span})
                
    return layer
    