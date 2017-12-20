from flask import render_template, jsonify, request
import os
import torch


def load_models(data_path):
    nn_path = os.path.join(data_path, "model.pth")
    model = torch.load(nn_path)

data_path = os.environ['CODEGEN_MODELS']
model, vocab = load_models(data_path)


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
