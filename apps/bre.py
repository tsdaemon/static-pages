from flask import render_template, jsonify, request
from tokenize_uk import *
import numpy as np
import os
import sys
import pickle
from itertools import permutations

if 'MITIE_HOME' in os.environ:
    mitie_path = os.environ['MITIE_HOME']
    sys.path.append(mitie_path)

from mitie import *

# load all models
data_path = os.environ['BRE_MODELS']
with open(data_path + '/people.person.parents.pkl', 'rb') as f:
    logreg_model = pickle.load(f)
mitie_model = binary_relation_detector(data_path + "/people.person.parents.svm")
ner = named_entity_extractor(data_path + "/uk_model.dat")


def static_bre_fn():
    return render_template('bre.html')


def api_bre_fn():
    """
    API function looking for all binary relations in text
    :param text:
    :return:
    """
    text = request.json[u'text']

    # split text on sentences
    sentences = [sent for paragraph in tokenize_text(text) for sent in paragraph]

    # look for relations in each sentence
    result = []
    for tokens in sentences:
        sent = {
            'tokens': tokens,
            'relations': []
        }

        encoded_tokens = [t.decode('utf-8') for t in tokens]

        # find entities
        entities = ner.extract_entities(encoded_tokens)
        entities = transform_entities(entities, tokens)
        sent['entities'] = entities

        # look for relation between each pair of persona entities
        persona_entities = filter(lambda e: e[1] == 'PERS', entities)
        for subj, obj in permutations(persona_entities, 2):
            rel = ner.extract_binary_relation(tokens, subj[0], obj[1])
            rel_val = mitie_model(rel)
            ret_val_proba = logreg_model.predict_proba(np.array([rel_val]).reshape(-1, 1))[:, 1]
            relation = {
                'object': obj,
                'subject': subj,
                'proba': ret_val_proba
            }
            sent['relations'].append(relation)

        result.append(sent)
        return jsonify(result)


def transform_entities(entities, tokens):
    """
    Restores entity text from tokens
    :param entities:
    :param tokens:
    :return:
    """
    for entity in entities:
        entity[4] = " ".join(tokens[i].decode() for i in entity[0])
    return entities
