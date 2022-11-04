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

    w = cfp.Selector(options=["var"], nickname_in="temp")
    w.button_pressed()  # make entry with default options
    assert w.vocab.vocab == {"temp": {"standard_name": "var$"}}
