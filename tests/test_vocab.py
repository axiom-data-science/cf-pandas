"""Test vocab"""

import os

from collections import defaultdict

import cf_pandas as cfp


def test_init():
    vocab = cfp.Vocab()
    assert isinstance(vocab.vocab, defaultdict)


def test_make_entry():
    vocab = cfp.Vocab()
    vocab.make_entry("temp", ["a", "b"], attr="name")
    assert vocab.vocab == {"temp": {"name": "a|b"}}


def test_add_vocabs():
    vocab = cfp.Vocab()
    vocab.make_entry("temp", ["a", "b"], attr="standard_name")
    vocab.make_entry("salt", ["a", "b"], attr="name")
    compare = {"temp": {"standard_name": "a|b|a|b"}, "salt": {"name": "a|b|a|b"}}
    assert (vocab + vocab).vocab == compare

    vocab2 = cfp.Vocab()
    vocab2.make_entry("temp", ["a", "b"], attr="name")
    compare = {
        "temp": {"name": "a|b", "standard_name": "a|b|a|b"},
        "salt": {"name": "a|b|a|b"},
    }
    assert (vocab + vocab2).vocab == compare


def test_make_more_entries():
    vocab = cfp.Vocab()
    vocab.make_entry("temp", ["a", "b"], attr="name")
    vocab.make_entry("temp", ["a", "b"], attr="standard_name")
    vocab.make_entry("salt", ["a", "b"], attr="name")
    vocab.make_entry("salt", ["a", "b"], attr="name")
    compare = {
        "temp": {"name": "a|b", "standard_name": "a|b"},
        "salt": {"name": "a|b|a|b"},
    }
    assert vocab.vocab == compare


def test_make_entry_with_Reg():
    reg1 = cfp.Reg(
        exclude=["abc", "123"],
        exclude_end=["def", "45"],
        exclude_start=["ghi", "67"],
        include=["jkl", "mno"],
        include_end="z",
        include_start="the",
    )
    vocab = cfp.Vocab()
    vocab.make_entry("words", reg1.pattern(), attr="name")
    assert vocab.vocab == {"words": {"name": reg1.pattern()}}
    reg2 = cfp.Reg(
        exclude=["abc", "45"],
        exclude_end=["def", "67"],
        exclude_start=["ghi", "123"],
        include=["jkl", "pr"],
        include_end="z",
        include_start="the",
    )
    vocab.make_entry("words", reg2.pattern(), attr="name")
    assert vocab.vocab == {"words": {"name": f"{reg1.pattern()}|{reg2.pattern()}"}}


def test_save_and_open(tmpdir):
    # save
    vocab = cfp.Vocab()
    vocab.make_entry("temp", ["a", "b"], attr="name")
    fname = f"{tmpdir}/testsave.json"
    vocab.save(fname)
    assert os.path.exists(fname) == 1

    # open
    vocab2 = cfp.Vocab(fname)
    assert vocab.vocab == vocab2.vocab
