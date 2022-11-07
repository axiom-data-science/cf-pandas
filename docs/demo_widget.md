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

# Widget to help humans select strings to match

The best way to understand this demo is with a Binder notebook since it includes a widget! Click on the badge to launch the Binder notebook.

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/axiom-data-science/cf-pandas/HEAD?labpath=docs/demo_widget.ipynb)

---

One way to deal with vocabularies (see [vocab demo](https://cf-pandas.readthedocs.io/en/latest/demo_vocab.html)) is to create a vocabulary that represents exactly which variables you want to match with for a given server. This way, when you are interacting with catalogs and data from that server you can be sure that your vocabulary will pull out the correct variables. It is essentially a variable mapping in this use case as opposed to a variable matching.

Sometimes the variables we want to search through for making selections could be very long. This widget is meant to help quickly include and exclude strings from the list and then allow for human-centered multi-select with command/control to export a vocabulary.

```{code-cell} ipython3
import cf_pandas as cfp
```

## Select from list of CF standard_names

You can read in all available standard_names with a utility in `cf-pandas` with:

`cfp.standard_names()`.

```{code-cell} ipython3
names = cfp.standard_names()
```

The basic idea is to write in a nickname for the variable you are representing in the top text box, and then select the standard_names that "count" as that variable. One problem is that if you don't include and exclude specific strings, the list of standard_names is too long to look through and select what you want for a given variable nickname.

Here is an example with a few inputs initialized to demonstrate. You can add more strings to exclude by adding them to the text box with a pipe ("|") between strings like `air|change`. You can pipe together terms to include also; the terms are treated as the logical "or" so the options list will show strings that have at least one of the "include" terms.

Once you narrow the options in the dropdown menu enough, you can select the standard_names you want. When you are happy with your selections, click "Press to save". This creates an entry in the class "vocab" of your variable nickname mapping to the attribute "standard_name" exactly matching each of the standard_names selected. Then, you can enter a new variable nickname and repeat the process to create another entry in the vocabulary.

```{code-cell} ipython3
w = cfp.Selector(options=names, nickname_in="temp",
                 exclude_in="air", include_in="temperature")

w.button_pressed()
```

The rest of the notebook shows results based on the user not changing anything in the widget so the results can be consistent.

Look at vocabulary

```{code-cell} ipython3
w.vocab
```

Save vocabulary for future use

```{code-cell} ipython3
w.vocab.save("std_name_demo")
```

Open and check out your vocab with:

```{code-cell} ipython3
cfp.Vocab("std_name_demo")
```
