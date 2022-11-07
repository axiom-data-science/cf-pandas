"""Test widget."""

import pytest

import cf_pandas as cfp


def test_init():
    cfp.Selector(options=["var1", "var2", "var3"])
    cfp.dropdown("temp", ["var1"])


def test_dropdown():
    # exclude var removes "var1"
    w = cfp.dropdown("temp", ["var1"], exclude="var")
    assert w.options == ()

    # include var includes only "var1"
    w = cfp.dropdown("temp", ["var1", "act2"], include="var")
    assert w.options[0] == "var1"


def test_selector():
    # cfp.Selector(options=["var1", "var2", "var3"])

    w = cfp.Selector(
        options=["var1", "var2", "act1", "act2"],
        nickname_in="temp",
        exclude_in="var",
        include_in="1",
    )
    w.button_pressed()  # make entry with default options
    assert w.vocab.vocab == {"temp": {"standard_name": "act1$"}}

    assert w.nickname == w.dropdown.widget.kwargs["nickname"] == "temp"


def test_selector_no_nickname():
    w = cfp.Selector(options=["var1", "var2", "act1", "act2"])
    with pytest.raises(KeyError):  # no nickname
        w.button_pressed()


def test_selector_input_vocab():
    vocab = cfp.Vocab()
    vocab.make_entry("key", ["var"])
    w = cfp.Selector(
        options=["var1", "var2", "act1", "act2"], vocab=vocab, nickname_in="key"
    )

    # initially contains input vocab
    assert w.vocab.vocab == {"key": {"standard_name": "var"}}

    # then make entry and change vocab
    w.button_pressed()  # make entry with default options — so only first valid value is kept
    assert w.vocab.vocab == {"key": {"standard_name": "var|var1$"}}
