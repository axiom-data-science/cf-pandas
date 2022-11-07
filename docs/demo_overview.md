---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.0
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# How to use `cf-pandas`

The main use of `cf-pandas` currently is for selecting a variable from a `pandas DataFrame` using the accessor and a custom vocabulary that searches column names for a match to the regular expressions. There are several class and utilities that support this functionality that are used internally but are also helpful for other packages.

```{code-cell} ipython3
import cf_pandas as cfp
import pandas as pd
```

## Select variable

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

vocab
```

### Get some data

```{code-cell} ipython3
# Some data
url = "https://files.stage.platforms.axds.co/axiom/netcdf_harvest/basis/2013/BE2013_/data.csv.gz"
df = pd.read_csv(url)
df
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
