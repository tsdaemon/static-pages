from flask import render_template, jsonify, request
import astor

import codegen.Constants as Constants
from codegen.preprocess import *
from codegen.lang.parse import *
from codegen.load import load_models

nn, grammar, terminal_vocab, vocab = load_models('./models/codegen')


def static_codegen_fn():
    return render_template('codegen.html')


def api_codegen_fn():
    """
    API function which converts NL query into Python code
    :param text:
    :return:
    """
    query = request.json[u'query']
    result = {}

    try:
        # tokenize text
        tokens, str_map = tokenize_and_strmap_query(query)

        indices = vocab.convertToIdx(tokens, Constants.UNK_WORD)

        # production model does not use trees
        cand_list = nn(None, indices, tokens)
        candidats = []
        for cid, cand in enumerate(cand_list[:10]):
            try:
                ast_tree = decode_tree_to_python_ast(cand.tree)
                code = astor.to_source(ast_tree)
                candidats.append(code)
            except:
                logging.debug("Exception in converting tree to code:"
                              "query: {}, beam pos: {}".format(query, cid))

        if len(candidats) > 0:
            code = candidats[0]
            for literal, place_holder in str_map.items():
                code = code.replace('\'' + place_holder + '\'', literal)
            result['code'] = code
        else:
            logging.error('No code generate for query: {}'.format(query))
            result['error'] = 'No code was generated for this query.'

    except Exception as e:
        logging.exception('Error occured during code generation for query: {}'.format(query), exc_info=e)
        result['error'] = 'Error occured during code generation for this query.'

    return jsonify(results=result)

