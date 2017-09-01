from flask import render_template, jsonify, request
from tokenize_uk import *
import numpy as np
import os
import sys
import pickle
from itertools import permutations
from langdetect import detect
from nltk.tokenize import sent_tokenize
from nltk import tokenize

if 'MITIE_HOME' in os.environ:
    mitie_path = os.environ['MITIE_HOME']
    sys.path.append(mitie_path)
from mitie import *


def en_tokenize(text):
    sents = sent_tokenize(text)
    return [[t.decode("utf-8") for t in tokenize(sent)] for sent in sents]


def uk_tokenize(text):
    return [sent for paragraph in tokenize_text(text) for sent in paragraph]

data_path = os.environ['BRE_MODELS']
with open(data_path + '/people.person.parents.pkl', 'rb') as f:
    logreg_model = pickle.load(f)


# load all models
def load_models():
    print("Loading models...")
    mitie_model_uk = binary_relation_detector(data_path + "/people.person.parents.svm")
    mitie_model_en = binary_relation_detector(data_path + "/rel_classifier_people.person.parents.svm")
    ner_uk = named_entity_extractor(data_path + "/uk_model.dat")
    ner_en = named_entity_extractor(data_path + "/en_model.dat")
    print("Models loaded.")
    return {
        'en': {
            'bre': mitie_model_en,
            'ner': ner_en,
            'tokenize': en_tokenize,
            'person_entity_type': 'PERSON'
        },
        'uk': {
            'bre': mitie_model_uk,
            'ner': ner_uk,
            'tokenize': uk_tokenize,
            'person_entity_type': 'PERS'
        }
    }

models = load_models()
supported_lang = ', '.join(models.keys())
print("Supported languages: {}.".format(supported_lang))


def static_bre_fn():
    return render_template('bre.html')


def api_bre_fn():
    """
    API function looking for all binary relations in text
    :param text:
    :return:
    """
    text = request.json[u'text']

    # detect language and select model
    lang = detect(text)
    if lang not in models:
        return language_not_supported_error(lang)
    model = models[lang]

    # tokenize
    sentences = model['tokenize'](text)

    # look for relations in each sentence
    result = []
    for tokens in sentences:
        sent = {
            'tokens': tokens,
            'relations': []
        }

        # find entities
        entities = model['ner'].extract_entities(tokens)
        sent['entities'] = list(map(lambda entity: transform_entity(entity, tokens), entities))

        # look for relation between each pair of persona entities
        persona_entities = filter(lambda e: e[1] == model['person_entity_type'], entities)
        for subj, obj in permutations(persona_entities, 2):
            find_relations(model, obj, sent, subj, tokens)

        result.append(sent)
    return jsonify(results=result)


def find_relations(model, obj, sent, subj, tokens):
    rel = model['ner'].extract_binary_relation(tokens, subj[0], obj[0])
    rel_val = model['bre'](rel)
    ret_val_proba = logreg_model.predict_proba(np.array([rel_val]).reshape(-1, 1))[:, 1]
    relation = {
        'object': transform_entity(obj, tokens),
        'subject': transform_entity(subj, tokens),
        'proba': ret_val_proba[0]
    }
    sent['relations'].append(relation)


def language_not_supported_error(lang):
    result = {'error': 'Language {} is not supported. Please use one of supported languages: {}.'.format(lang,
                                                                                                         supported_lang)}
    return jsonify(results=result)


def transform_entity(entity, tokens):
    """
    Restores entity text from tokens
    :param entities:
    :param tokens:
    :return:
    """
    return {
        'text': " ".join(tokens[i] for i in entity[0]),
        'type': entity[1],
        'range': [i for i in entity[0]]
    }
