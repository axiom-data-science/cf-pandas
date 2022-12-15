"""Class for creating and working with vocabularies."""

import json
import pathlib
from collections import defaultdict
from typing import DefaultDict, Dict, Optional, Sequence, Union

from .utils import astype


class Vocab(object):
    """Class to handle vocabularies."""

    def __init__(self, openname: Optional[str] = None):
        self.vocab: DefaultDict[str, Dict[str, str]]
        if openname is not None:
            self.vocab = defaultdict(dict, self.open_file(openname))
        else:
            self.vocab = defaultdict(dict)

    def __repr__(self):
        """Representation."""
        return dict(self.vocab).__repr__()

    def make_entry(
        self, nickname: str, expressions: Union[str, list], attr: str = "standard_name"
    ):
        """Make an entry for vocab.

        Parameters
        ----------
        nickname: str
            The nickname to call the variable being represented in this entry.
        expressions: str, list
            Regular expression(s) to use to select out the variable in a regex match. Multiple expressions input in a list are piped together to create one str of expressions.
        attr: str
            What attribute to identify the regular expressions with. Default is "standard_name", but other reasonable options are any variable attributes in a netcdf file such as "units", "name", and "long_name".

        Examples
        --------

        The following creates an entry in the vocabulary stored in `vocab.vocab`. It doesn't print the entry but it has been pasted in below the example to show what it looks like.

        >>> import cf_pandas as cfp
        >>> vocab = cfp.Vocab()
        >>> vocab.make_entry("temp", ["a","b"], attr="name")
        {'temp': {'standard_name': 'a|b'}})
        """

        expressions = astype(expressions, list)
        entry: DefaultDict[str, Dict[str, str]] = defaultdict(dict)
        entry[nickname][attr] = "|".join(expressions)
        self.__iadd__(entry)

        return self

    def add(
        self, other_vocab: Union[DefaultDict[str, Dict[str, str]], "Vocab"], method: str
    ) -> "Vocab":
        """Add two Vocab objects together...

        by adding their `.vocab`s together. Expressions are piped together but otherwise not changed.
        This is used for both `__add__` and `__iadd__`.

        Parameters
        ----------
        other_vocab: Vocab
            Other Vocab object to combine with.
        method : str
            Whether to run as "add" which returns a new Vocab object or "iadd" which adds to the original object.

        Returns
        -------
        Vocab
            vocab + other_vocab either as a new object or in place.
        """

        if isinstance(other_vocab, Vocab):
            other_vocab = other_vocab.vocab

        if method == "add":
            output = Vocab()
        elif method == "iadd":
            output = self

        nicknames = set(list(self.vocab.keys()) + list(other_vocab.keys()))
        for nickname in nicknames:

            # gather all attributes under nickname as a set to compare their expressions
            attributes = set(
                list(self.vocab[nickname].keys()) + list(other_vocab[nickname].keys())
            )

            # pipe together expressions for nickname-attribute pairs
            for attribute in attributes:
                new_expressions = (
                    self.vocab[nickname].get(attribute, "")
                    + "|"
                    + other_vocab[nickname].get(attribute, "")
                ).strip("|")
                output.vocab[nickname][attribute] = new_expressions
        return output

    def __add__(self, other_vocab: Union[DefaultDict[str, Dict[str, str]], "Vocab"]):
        """vocab1 + vocab2"""
        return self.add(other_vocab, "add")

    def __iadd__(self, other_vocab: Union[DefaultDict[str, Dict[str, str]], "Vocab"]):
        """vocab1 += vocab2"""
        return self.add(other_vocab, "iadd")

    def __radd__(
        self, other_vocab: Union[DefaultDict[str, Dict[str, str]], "Vocab"]
    ) -> "Vocab":
        """right add?"""
        return self.__add__(other_vocab)

    def save(self, savename: Union[str, pathlib.PurePath]):
        """Save to file.

        Parameters
        ----------
        savename: str, PurePath
            Filename to save to.
        """
        a_file = open(astype(savename, pathlib.PurePath).with_suffix(".json"), "w")
        json.dump(self.vocab, a_file)
        a_file.close()

    def open_file(self, openname: Union[str, pathlib.PurePath]):
        """Open previously-saved vocab.

        Parameters
        ----------
        openname: str
            Where to find vocab to open.
        """
        return json.loads(
            open(pathlib.PurePath(openname).with_suffix(".json"), "r").read()
        )


def merge(vocabs: Sequence[Vocab]) -> Vocab:
    """Add together multiple Vocab objects.

    Parameters
    ----------
    vocabs : Sequence[Vocab]
        Sequence of Vocab objects to merge.

    Returns
    -------
    Vocab
        Single Vocab object made up of input vocabs.
    """

    final_vocab = Vocab()
    for vocab in vocabs:
        final_vocab += vocab
    return final_vocab
