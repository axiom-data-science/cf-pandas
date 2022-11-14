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

# `Reg`: Write Regular Expressions

This class will help you write simple regular expressions. The available options are:

These all work as logical "or" if there is more than one string specified:
* `exclude` (string or list)
* `exclude_start` (string or list)
* `exclude_end` (string or list)

Also:
* `include` (logical "and", string or list)
* `include_or` (logical "or", string or list)
* `include_exact` (string)
* `include_start` (string)
* `include_end` (string)
* and `ignore_case` (bool)

If you find you want to use more than one `include_exact`, `include_start`, or `include_end` at once, you should write a new regular expression with the class, instead. That is, write multiple expressions and pipe them together with a pipe between, like:

`"expression1|expression2"`

rather than try to get everything into a single expression, or just use the built-in convenience function:

`cfp.joinpat([reg1, reg2])`


**Note:** you may need to use Python package `regex` instead of `re` with piped-together expressions.

```{code-cell} ipython3
import cf_pandas as cfp
import regex
```

## Write a regular expression

```{code-cell} ipython3
reg = cfp.Reg(include="one", exclude="two")
reg.pattern()
```

```{code-cell} ipython3
[string for string in ["onetwo","twothree","onethree"] if regex.match(reg.pattern(), string)]
```
