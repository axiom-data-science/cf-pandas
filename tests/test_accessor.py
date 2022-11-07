"""Test cf-pandas."""

import pandas as pd
import pytest

import cf_pandas as cfp


criteria = {
    "wind_s": {
        "standard_name": "wind_speed$",
    },
}


def test_options():
    # test for inputting a nonexistent option
    with pytest.raises(ValueError):
        cfp.set_options(DISPLAY_WIDTH=80)


def test_match_criteria_key_accessor():

    vals = ["wind_speed", "WIND_SPEED", "wind_speed_status"]

    df = pd.DataFrame(columns=["temp", "wind_speed"])

    # test accessor with set_options criteria
    with cfp.set_options(custom_criteria=criteria):
        assert df.cf["wind_s"].columns == ["wind_speed"]
