from flask import render_template, jsonify, request
import astor
import torch
import numpy as np
import random
import os
import sys
import nltk

import Constants
from lang.parse import *
from natural_lang.vocab import Vocab
cuda = True


def load_models(data_path):
    logging.info('Loading codegen models...')

    nn_file = os.path.join(data_path, "model.pth")
    vocab_file = os.path.join(data_path, "vocab.txt")
    terminal_vocab_file = os.path.join(data_path, "terminal_vocab.txt")
    # grammar_file = os.path.join(data_path, "grammar.txt.bin")

    device_map = lambda storage, loc: storage.cuda() if cuda else lambda storage, loc: storage
    nn = torch.load(nn_file, device_map)
    nn.eval()
    # with open(grammar_file, 'rb') as f:
    #     grammar = pickle.load(f)
    terminal_vocab = Vocab(terminal_vocab_file, data=[Constants.UNK_WORD, Constants.EOS_WORD, Constants.PAD_WORD])
    vocab = Vocab(vocab_file, data=[Constants.UNK_WORD, Constants.EOS_WORD, Constants.PAD_WORD])

    logging.info('Codegen models loaded.')
    return nn, None, terminal_vocab, vocab

nn, grammar, terminal_vocab, vocab = load_models('./models/codegen')
RANDOM_SEED = 181783
np.random.seed(RANDOM_SEED)
torch.manual_seed(RANDOM_SEED)
random.seed(RANDOM_SEED)


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
        code = gen_code(query)
        result['code'] = code
    except Exception as e:
        logging.exception('Error occured during code generation for query: {}'.format(query), exc_info=e)
        result['error'] = 'Error occured during code generation for this query.'

    return jsonify(results=result)


QUOTED_STRING_RE = re.compile(r"(?P<quote>['\"])(?P<string>.*?)(?<!\\)(?P=quote)")
def tokenize_and_strmap_query(query):
    """
    replace strings in query to a special place holder
    """
    str_count = 0
    str_map = dict()

    matches = QUOTED_STRING_RE.findall(query)
    # de-duplicate
    cur_replaced_strs = set()
    for match in matches:
        # If one or more groups are present in the pattern,
        # it returns a list of groups
        quote = match[0]
        str_literal = quote + match[1] + quote

        if str_literal in cur_replaced_strs:
            continue

        # FIXME: substitute the ' % s ' with
        if str_literal in ['\'%s\'', '\"%s\"']:
            continue

        str_repr = '_STR_%d_' % str_count
        str_map[str_literal] = str_repr

        query = query.replace(str_literal, str_repr)

        str_count += 1
        cur_replaced_strs.add(str_literal)

    # tokenize
    query_tokens = nltk.word_tokenize(query)

    new_query_tokens = []
    # break up function calls like foo.bar.func
    for token in query_tokens:
        new_query_tokens.append(token)
        i = token.find('.')
        if 0 < i < len(token) - 1:
            new_tokens = ['('] + token.replace('.', ' ').split(' ') + [')']
            new_query_tokens.extend(new_tokens)

    return new_query_tokens, str_map


def gen_code(query):
    # tokenize text
    tokens, str_map = tokenize_and_strmap_query(query)

    indices = vocab.convertToIdx(tokens, Constants.UNK_WORD)

    indices_tensor = torch.LongTensor(indices)
    if cuda:
        indices_tensor = indices_tensor.cuda()

    # production model does not use trees
    cand_list = nn(None, indices_tensor, tokens)
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
        return code
    else:
        raise Exception('No code was generated for query {}.'.format(query))


# interactive mode
if __name__ == '__main__':
    query = sys.argv[1]
    print("Generating code for query: {}".format(query))
    code = gen_code(query)
    print("Generated code: {}".format(code))
