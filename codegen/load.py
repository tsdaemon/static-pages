import logging
import torch
import pickle
import os
import sys

from codegen.natural_lang.vocab import Vocab
import codegen.Constants as Constants

import codegen.nn as model
import codegen.natural_lang as natural_lang
import codegen.lang as lang


def load_models(data_path):
    logging.info('Loading codegen models...')
    sys.modules['model'] = model
    sys.modules['natural_lang'] = natural_lang
    sys.modules['lang'] = lang

    nn_file = os.path.join(data_path, "model.pth")
    vocab_file = os.path.join(data_path, "vocab.txt")
    terminal_vocab_file = os.path.join(data_path, "terminal_vocab.txt")
    grammar_file = os.path.join(data_path, "grammar.txt.bin")

    nn = torch.load(nn_file, lambda storage, loc: storage)
    # grammar = pickle.load(grammar_file)
    terminal_vocab = Vocab(terminal_vocab_file, data=[Constants.UNK_WORD, Constants.EOS_WORD, Constants.PAD_WORD])
    vocab = Vocab(vocab_file, data=[Constants.UNK_WORD, Constants.EOS_WORD, Constants.PAD_WORD])

    del sys.modules['model']
    del sys.modules['natural_lang']
    del sys.modules['lang']
    logging.info('Codegen models loaded.')
    return nn, None, terminal_vocab, vocab
