from estnltk_core.converters.default_serialisation import dict_to_layer as default_dict_to_layer

from typing import Union

from estnltk_core.layer.base_layer import to_base_span
from estnltk_core.layer.layer import Layer
from estnltk import Span 

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
    attributes = []
    for attr in layer.attributes:
        if attr == "root":
            if len(layer[attr])!=0 and type(layer[attr][0])!=Span:
                attributes.append(attr)
        elif attr not in {'parent_span', 'children'}:
            attributes.append(attr)

    for span in layer:
        annotation_dict = [{attr: annotation[attr] for attr in attributes} for annotation in span.annotations]
        spans.append({'base_span': span.base_span.raw(),
                      'annotations': annotation_dict})
    layer_dict['spans'] = spans

    return layer_dict


def dict_to_layer(layer_dict: dict, text_object=None):
    from estnltk.taggers.standard.syntax.syntax_dependency_retagger import SyntaxDependencyRetagger
    layer = default_dict_to_layer(layer_dict, text_object)
    
    for span in layer:
        for annotation in span.annotations:
            annotation["root"] = text_object[layer.enveloping].spans[annotation["root_id"]-1]
                
    return layer
    
