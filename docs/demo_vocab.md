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

# `Vocab`: manage custom vocabularies

Custom vocabularies are used in `cf-xarray` and `cf-pandas` to search variable names and available metadata (in the case of `cf-xarray` with Dataset variable attributes) and compare with regular expressions to make selections. These make it possible to generically select variables from different Datasets and DataFrames. However, they are difficult to write, handle, and maintain, and control which variables are found so being able to tweak them is important.

```{code-cell} ipython3
import cf_pandas as cfp
import regex
```

## What does a custom vocabulary look like?

### `cf-xarray`
For a netcdf-style Dataset, this criteria dictionary will be used to search over the attributes in each variable and compare with the regular expressions to search for matches, in this case checking specifically the variable `standard_name` and `name`. There will be a match to the nickname "ssh" if the `standard_name` for a variable is exactly "sea_surface_height" or if the `standard_name` contains the string "sea_surface_elevation".

### `cf-pandas`
`cf-pandas` is made to access `pandas` DataFrames in an analogous manner to using the `cf-xarray` accessor with Datasets. DataFrames do not have attributes to compare with, only the column name. So, every regular expression for a given nickname (in the example given, "ssh" and "temp"), will be compared with the column name. The extra dictionary structure is maintained in this case so that vocabularies can be used between `cf-xarray` and `cf-pandas` if needed, for example, to select a model variable and compare it with a data file variable.

```{code-cell} ipython3
criteria = {
    "ssh": {
        "standard_name": "sea_surface_height$|sea_surface_elevation",
        "name": "(?i)sea_surface_elevation(?!.*?_qc)"
    },
    "temp": {
        "standard_name": "sea_water_temperature",
        "name": "(?i)temperature(?!.*(skin|ground|air|_qc))"
    },
}
criteria
```

## How should I use the custom vocabulary?

You can set your vocabulary to be used generally, or use with a context-manager. I recommend using the context-manager approach whenever you might use more than one vocabulary.

To set it generally for, for example, `cf-xarray`, you would do:

```cf_xarray.set_options(custom_criteria=criteria)```

or for `cf-pandas`, imported as `cfp`:

```cfp.set_options(custom_criteria=criteria)```

In this demo, we will use the context manager approach so that we can use more than one vocabulary. For example, here we compare a list of strings with the vocabulary we called `criteria` and are searching for all matches in the list to the variable by the nickname "ssh".

```{code-cell} ipython3
vals = ["zeta", "sea_surface_height", "sea_surface", "sea_surface_elevation_zeta"]

with cfp.set_options(custom_criteria=criteria):
    print(cfp.match_criteria_key(vals, "ssh"))
```

## How can I make a custom vocabulary? Introducing the Vocab class.

As you can see, making `criteria` could be labor intensive. Also, users may want to create more than one of these and use them separately or together in different circumstances, and save them for later. That is what the `Vocab` class in `cf-pandas` is meant to help with.

In this example, we make an entry in our vocabulary that has two regular expressions in it to start.

```{code-cell} ipython3
# initialize class
vocab1 = cfp.Vocab()

# Make an entry to add to your vocabulary
vocab1.make_entry("new_variable_nickname", ["match_this_exactly$", "match_that_exactly$"], attr="name")
```

Retrieve the vocabulary you've made with `vocab1.vocab`:

```{code-cell} ipython3
vocab1.vocab
```

And you can subsequently add other entries:

```{code-cell} ipython3
# add another entry
vocab1.make_entry("new_variable_nickname", ["match_this_string", "match_that_exactly$"], attr="long_name")

# add another entry
vocab1.make_entry("other_variable_nickname", "match_that_string", attr="standard_name")
```

```{code-cell} ipython3
vocab1
```

Test our new vocabulary:

```{code-cell} ipython3
vals = ["match_this_exactly", "match_this_exactly_but", "other_variable_nickname", "match_that_string"]

with cfp.set_options(custom_criteria=vocab1.vocab):
    print(cfp.match_criteria_key(vals, "new_variable_nickname"))
```

## Working with vocabularies

+++

### Save to file

Save your new vocabulary to a file with:

`vocab1.save(filename)`

+++

### Read from file

Retrieve your previously-saved vocabulary by inputting the path into a new instantiation of the Vocab class with:

`vocab_read = cfp.Vocab(filepath)`

+++

### Combine

```{code-cell} ipython3
vocab1 = cfp.Vocab()
vocab1.make_entry("new_variable_nickname", ["match_this_exactly$", "match_that_exactly$"], attr="name")

vocab2 = cfp.Vocab()
vocab2.make_entry("new_variable_nickname", ["match_this_string", "match_that_exactly$"], attr="long_name")
vocab2.make_entry("other_variable_nickname", "match_that_string", attr="standard_name")

vocab1 + vocab2
```

Merge 2 or more Vocab objects:

```{code-cell} ipython3
cfp.merge([vocab1, vocab2])
```

Can also add in place

```{code-cell} ipython3
# also works
vocab1 += vocab2
```

## Use the `Reg` class to write regular expressions

We used simple exact matching regular expressions above, but for anything more complicated it can be hard to write regular expressions. You can use the `Reg` class in `cf-pandas` to write regular expressions with several options, as demonstrated more in [another doc page](https://cf-pandas.readthedocs.io/en/latest/demo_reg.html), and briefly here.

```{code-cell} ipython3
# initialize class
vocab = cfp.Vocab()

# define a regular expression to represent your variable
reg = cfp.Reg(include="temperature", exclude="air", exclude_end="_qc", include_start="sea")

# Make an entry to add to your vocabulary
vocab.make_entry("temp", reg.pattern(), attr="standard_name")

vocab
```
