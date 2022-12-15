---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.0
kernelspec:
  display_name: Python 3.10.6 ('cf-pandas')
  language: python
  name: python3
---

# How to use `cf-pandas`

The main use of `cf-pandas` currently is for selecting columns of a DataFrame that represent axes or coordinates of the dataset and for selecting a variable from a `pandas DataFrame` using the accessor and a custom vocabulary that searches column names for a match to the regular expressions, as well as some other capabilities that have been ported over from `cf-xarray`. There are several class and utilities that support this functionality that are used internally but are also helpful for other packages.

```{code-cell} ipython3
import cf_pandas as cfp
import pandas as pd
```

## Get some data

```{code-cell} ipython3
# Some data
url = "https://files.stage.platforms.axds.co/axiom/netcdf_harvest/basis/2013/BE2013_/data.csv.gz"
df = pd.read_csv(url)
df
```

## Basic accessor usage

The terminology all comes from `cf-xarray` which deals with multi-dimensional data and has more layers of standardized attributes. This package ports over useful functionality, retaining some of the complexity of terminology and syntax from `cf-xarray` which doesn't always apply. The perspective is to be able to think about and use DataFrames of data in a similar manner to Datasets of data/model output.

When you use the `cf-pandas` accessor it will first validate that columns representing time, latitude, and longitude are present and identifiable (by validating the object).

Using an approach copied directly from `cf-xarray`, `cf-pandas` contains a mapping of names from the CF conventions that define the axes ("T", "Z", "Y", "X") and coordinates ("time", "vertical", "latitude", "longitude"). These are built in and used to identify columns containing axes and coordinates using name matching (column names are split by white space for the comparison).

Check axes and coordinates mappings of the dataset:

```{code-cell} ipython3
df.cf.axes, df.cf.coordinates
```

Check all available keys:

```{code-cell} ipython3
df.cf.keys()
```

Is a certain key in the DataFrame?

```{code-cell} ipython3
"T" in df.cf, "X" in df.cf
```

What CF standard names can be identified with strict matching in the column names? Column names will be split by white space for this comparison.

```{code-cell} ipython3
df.cf.standard_names
```

## Select variable

Selecting a variable typically requires knowing the name of the column representing the variable. What is demonstrated here is an approach to selecting a column name containing the variable using regular expression matching. In this case, the user defines the regular expression matching that will be used to identify matches to a variable. There are helper functions for this process available in `cf-pandas`; see the `Reg`, `Vocab`, and `widget` classes and below for more information.

+++

### Create custom vocabulary

More information about custom vocabularies and using the `Vocab` class here: https://cf-pandas.readthedocs.io/en/latest/demo_vocab.html

You can make regular expressions for your vocabulary by hand or use the `Reg` class in `cf-pandas` to do so.

```{code-cell} ipython3
# initialize class
vocab = cfp.Vocab()

# define a regular expression to represent your variable
reg = cfp.Reg(include="salinity", exclude="soil", exclude_end="_qc")

# Make an entry to add to your vocabulary
vocab.make_entry("salt", reg.pattern(), attr="standard_name")

# Add another entry to vocab
vocab.make_entry("temp", "temp")

vocab
```

### Access variable

Refer to the column of data you want by the nickname described in your custom vocabulary.

You can do this with a context manager, especially if you are using more than one vocabulary:

```{code-cell} ipython3
with cfp.set_options(custom_criteria=vocab.vocab):
    print(df.cf["salt"])
```

Or you can set one for use generally in this kernel:

```{code-cell} ipython3
cfp.set_options(custom_criteria=vocab.vocab)
df.cf["salt"]
```

Display mapping of all variables in the dataset that can be identified using the custom criteria/vocab we defined above:

```{code-cell} ipython3
df.cf.custom_keys
```

## Other utilities

+++

### Access all CF Standard Names

```{code-cell} ipython3
sn = cfp.standard_names()
sn[:5]
```

### Use vocabulary to match any list

This is the logic under the hood of the `cf-pandas` accessor that selects what column matches a variable nickname according to the custom vocabulary. This comes from `cf-xarray` almost exactly. It is available as a separate function because it is useful to use in other scenarios too. Here we filter the standard names just found by our custom vocabulary from above.

```{code-cell} ipython3
cfp.match_criteria_key(sn, "salt", vocab.vocab)
```
