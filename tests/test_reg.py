"""Test Reg class."""

import pandas as pd
import pytest

from pandas import testing as tm

import cf_pandas as cfp


strings = [
    "sea_water_temperature",
    "sea_water_temperature [celsius]",
    "water_temperature",
    "temperature_qc",
]
df = cfp.astype(strings, pd.Series)


def test_exclude():
    reg = cfp.Reg(exclude="qc")
    dfmatch = df[df.str.match(reg.pattern())]
    matches = [
        "sea_water_temperature",
        "sea_water_temperature [celsius]",
        "water_temperature",
    ]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)

    # make sure this approach yields identical results, and use lists too
    reg2 = cfp.Reg()
    reg2.exclude(["qc"])
    dfmatch2 = df[df.str.match(reg2.pattern())]
    tm.assert_series_equal(dfmatch, dfmatch2, check_index=False)

    # make sure inputting None and "" both yield the full list
    reg3 = cfp.Reg(exclude=None)
    dfmatch3 = df[df.str.match(reg3.pattern())]
    tm.assert_series_equal(dfmatch3, df, check_index=False)

    reg4 = cfp.Reg(exclude="")
    dfmatch4 = df[df.str.match(reg4.pattern())]
    tm.assert_series_equal(dfmatch4, df, check_index=False)


def test_exclude_two():
    reg = cfp.Reg(exclude=["qc", "sea"])
    dfmatch = df[df.str.match(reg.pattern())]
    matches = ["water_temperature"]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)


def test_include_exact():
    reg = cfp.Reg(include_exact="water_temperature")
    dfmatch = df[df.str.match(reg.pattern())]
    matches = ["water_temperature"]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)

    reg = cfp.Reg()
    reg.include_exact("water_temperature")
    dfmatch2 = df[df.str.match(reg.pattern())]
    tm.assert_series_equal(dfmatch, dfmatch2, check_index=False)


def test_include_exact_two():
    reg = cfp.Reg(include_exact="sea_water_temperature")
    with pytest.raises(ValueError):
        reg.include_exact("qc")


def test_include_exact_list():
    with pytest.raises(TypeError):
        reg = cfp.Reg(include_exact=["sea_water_temperature"])


def test_include():
    reg = cfp.Reg(include="temperature")
    dfmatch = df[df.str.match(reg.pattern())]
    tm.assert_series_equal(dfmatch, df, check_index=False)

    reg = cfp.Reg()
    reg.include("temperature")
    dfmatch2 = df[df.str.match(reg.pattern())]
    tm.assert_series_equal(dfmatch, dfmatch2, check_index=False)

    reg = cfp.Reg(include_or="temperature")
    dfmatch_or = df[df.str.match(reg.pattern())]
    tm.assert_series_equal(dfmatch, dfmatch_or, check_index=False)

    reg = cfp.Reg()
    reg.include_or("temperature")
    dfmatch_or2 = df[df.str.match(reg.pattern())]
    tm.assert_series_equal(dfmatch, dfmatch_or2, check_index=False)


def test_include_two():
    reg = cfp.Reg(include=["water", "temp"])
    dfmatch = df[df.str.match(reg.pattern())]
    matches = [
        "sea_water_temperature",
        "sea_water_temperature [celsius]",
        "water_temperature",
    ]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)


def test_include_or_two():
    reg = cfp.Reg(include_or=["qc", "celsius"])
    dfmatch = df[df.str.match(reg.pattern())]
    matches = ["sea_water_temperature [celsius]", "temperature_qc"]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)


def test_include_end():
    reg = cfp.Reg(include_end="temperature")
    dfmatch = df[df.str.match(reg.pattern())]
    matches = ["sea_water_temperature", "water_temperature"]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)

    reg = cfp.Reg()
    reg.include_end("temperature")
    dfmatch2 = df[df.str.match(reg.pattern())]
    tm.assert_series_equal(dfmatch, dfmatch2, check_index=False)


def test_include_end_two():
    reg = cfp.Reg(include_end="sea_water_temperature")
    with pytest.raises(ValueError):
        reg.include_end("qc")


def test_include_end_list():
    with pytest.raises(TypeError):
        reg = cfp.Reg(include_end=["sea_water_temperature"])


def test_exclude_include():
    reg = cfp.Reg(exclude="qc", include="sea_water_temperature")
    dfmatch = df[df.str.match(reg.pattern())]
    matches = ["sea_water_temperature", "sea_water_temperature [celsius]"]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)

    reg = cfp.Reg(exclude="qc", include_or=["sea", "temp"])
    dfmatch = df[df.str.match(reg.pattern())]
    matches = [
        "sea_water_temperature",
        "sea_water_temperature [celsius]",
        "water_temperature",
    ]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)

    reg = cfp.Reg(exclude="qc", include=["sea", "temp"])
    dfmatch = df[df.str.match(reg.pattern())]
    matches = ["sea_water_temperature", "sea_water_temperature [celsius]"]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)


def test_exclude_include_end():
    reg = cfp.Reg(exclude="sea", include_end="temperature")
    dfmatch = df[df.str.match(reg.pattern())]
    matches = ["water_temperature"]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)


def test_exclude_include_exact():
    with pytest.raises(ValueError):
        reg = cfp.Reg(exclude="sea", include_exact="temperature")


def test_include_include_exact():
    with pytest.raises(ValueError):
        reg = cfp.Reg(include="sea", include_exact="temperature")


def test_include_end_include_exact():
    with pytest.raises(ValueError):
        reg = cfp.Reg(include_end="sea", include_exact="temperature")


def test_include_include_end():
    reg = cfp.Reg(include="sea", include_end="temperature")
    dfmatch = df[df.str.match(reg.pattern())]
    matches = ["sea_water_temperature"]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)


def test_include_start():
    reg = cfp.Reg(include_start="temperature")
    dfmatch = df[df.str.match(reg.pattern())]
    matches = ["temperature_qc"]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)

    reg = cfp.Reg()
    reg.include_start("temperature")
    dfmatch2 = df[df.str.match(reg.pattern())]
    tm.assert_series_equal(dfmatch, dfmatch2, check_index=False)


def test_include_start_two():
    reg = cfp.Reg(include_start="sea_water_temperature")
    with pytest.raises(ValueError):
        reg.include_start("qc")


def test_include_start_list():
    with pytest.raises(TypeError):
        reg = cfp.Reg(include_start=["sea_water_temperature"])


def test_exclude_include_start():
    reg = cfp.Reg(exclude="celsius", include_start="sea")
    dfmatch = df[df.str.match(reg.pattern())]
    matches = ["sea_water_temperature"]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)


def test_include_start_include_exact():
    with pytest.raises(ValueError):
        reg = cfp.Reg(include_start="sea", include_exact="temperature")


def test_include_include_start():
    reg = cfp.Reg(include="celsius", include_start="sea")
    dfmatch = df[df.str.match(reg.pattern())]
    matches = ["sea_water_temperature [celsius]"]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)


def test_exclude_start():
    reg = cfp.Reg(exclude_start="sea")
    dfmatch = df[df.str.match(reg.pattern())]
    matches = ["water_temperature", "temperature_qc"]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)

    reg = cfp.Reg()
    reg.exclude_start("sea")
    dfmatch2 = df[df.str.match(reg.pattern())]
    tm.assert_series_equal(dfmatch, dfmatch2, check_index=False)


def test_exclude_start_two():
    reg = cfp.Reg(exclude_start=["water", "sea"])
    dfmatch = df[df.str.match(reg.pattern())]
    matches = ["temperature_qc"]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)


def test_exclude_start_include():
    reg = cfp.Reg(exclude_start="sea", include="temperature")
    dfmatch = df[df.str.match(reg.pattern())]
    matches = ["water_temperature", "temperature_qc"]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)

    reg = cfp.Reg(
        exclude_start=["water", "temperature"], include_or=["temp", "celsius"]
    )
    dfmatch = df[df.str.match(reg.pattern())]
    matches = ["sea_water_temperature", "sea_water_temperature [celsius]"]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)

    reg = cfp.Reg(exclude_start=["water", "temperature"], include=["temp", "celsius"])
    dfmatch = df[df.str.match(reg.pattern())]
    matches = ["sea_water_temperature [celsius]"]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)


def test_exclude_start_include_end():
    reg = cfp.Reg(exclude_start="sea", include_end="qc")
    dfmatch = df[df.str.match(reg.pattern())]
    matches = ["temperature_qc"]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)


def test_exclude_start_include_exact():
    with pytest.raises(ValueError):
        reg = cfp.Reg(exclude_start="sea", include_exact="temperature")


def test_exclude_start_include_start():
    reg = cfp.Reg(exclude_start="sea", include_start="water")
    dfmatch = df[df.str.match(reg.pattern())]
    matches = ["water_temperature"]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)


def test_exclude_end():
    reg = cfp.Reg(exclude_end="temperature")
    dfmatch = df[df.str.match(reg.pattern())]
    matches = ["sea_water_temperature [celsius]", "temperature_qc"]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)

    reg = cfp.Reg()
    reg.exclude_end("temperature")
    dfmatch2 = df[df.str.match(reg.pattern())]
    tm.assert_series_equal(dfmatch, dfmatch2, check_index=False)


def test_exclude_end_two():
    reg = cfp.Reg(exclude_end=["temperature", "qc"])
    dfmatch = df[df.str.match(reg.pattern())]
    matches = ["sea_water_temperature [celsius]"]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)

    reg = cfp.Reg(exclude_end=["temperature", r"\[celsius\]"])
    dfmatch = df[df.str.match(reg.pattern())]
    matches = ["temperature_qc"]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)


def test_exclude_end_include():
    reg = cfp.Reg(exclude_end="temperature", include="celsius")
    dfmatch = df[df.str.match(reg.pattern())]
    matches = ["sea_water_temperature [celsius]"]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)

    reg = cfp.Reg(exclude_end="temperature", include_or=["temp", "celsius"])
    dfmatch = df[df.str.match(reg.pattern())]
    matches = ["sea_water_temperature [celsius]", "temperature_qc"]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)

    reg = cfp.Reg(exclude_end="temperature", include=["temp", "celsius"])
    dfmatch = df[df.str.match(reg.pattern())]
    matches = ["sea_water_temperature [celsius]"]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)


def test_exclude_end_include_end():
    reg = cfp.Reg(exclude_end="temperature", include_end="qc")
    dfmatch = df[df.str.match(reg.pattern())]
    matches = ["temperature_qc"]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)


def test_exclude_end_include_exact():
    with pytest.raises(ValueError):
        reg = cfp.Reg(exclude_end="sea", include_exact="temperature")


def test_exclude_end_include_start():
    reg = cfp.Reg(exclude_end="temperature", include_start="temperature")
    dfmatch = df[df.str.match(reg.pattern())]
    matches = ["temperature_qc"]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)


def test_exclude_start_end():
    reg = cfp.Reg(
        exclude_end=r"\[celsius\]", exclude_start="temperature", exclude="sea"
    )
    dfmatch = df[df.str.match(reg.pattern())]
    matches = ["water_temperature"]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)


def test_include_start_end():
    reg = cfp.Reg(include_or=["water", "celsius"], exclude="qc", include_start="sea")
    dfmatch = df[df.str.match(reg.pattern())]
    matches = ["sea_water_temperature", "sea_water_temperature [celsius]"]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)

    reg = cfp.Reg(include=["water", "celsius"], exclude="qc", include_start="sea")
    dfmatch = df[df.str.match(reg.pattern())]
    matches = ["sea_water_temperature [celsius]"]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)


def test_exclude_start_end_include_start_end():
    reg = cfp.Reg(
        exclude_start="temperature",
        exclude="celsius",
        include="water",
        include_start="sea",
    )
    dfmatch = df[df.str.match(reg.pattern())]
    matches = ["sea_water_temperature"]
    tm.assert_series_equal(dfmatch, pd.Series(matches), check_index=False)
