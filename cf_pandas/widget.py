"""Widget"""

from typing import DefaultDict, Dict, Optional, Sequence, Union

import ipywidgets as widgets
import pandas as pd

from .reg import Reg
from .utils import astype
from .vocab import Vocab


def dropdown(
    nickname: str,
    options: Union[Sequence, pd.Series],
    include: str = "",
    exclude: str = "",
):
    """Makes widget that is used by class.

    Options are filtered by a regular expression written to reflect the include and exclude inputs, and these are updated when changed and shown in the dropdown. The user should select using `command` or `control` to make multiple options. Then push the "save" button when the nickname and selected options from the dropdown menu are the variables you want to include exactly in a future regular expression search.

    Parameters
    ----------
    nickname: str
        nickname to associate with the Vocab class vocabulary entry from this, e.g., "temp"
    options: Sequence
        strings to select from in the dropdown widget. Will be filtered by include and exclude inputs.
    include: str
        include must be in options values for them to show in the dropdown. Will update as more are input. To input more than one, join separate strings with "|". For example, to search on both "temperature" and "sea_water", input "temperature|sea_water".
    exclude: str
        exclude must not be in options values for them to show in the dropdown. Will update as more are input. To input more than one, join separate strings with "|". For example, to exclude both "temperature" and "sea_water", input "temperature|sea_water".
    """

    reg = Reg(include=include, exclude=exclude)
    print(reg.pattern())
    options = astype(options, pd.Series)
    options = options[options.str.match(reg.pattern())]

    widg = widgets.SelectMultiple(
        options=options,
        value=[] if len(options) == 0 else [options[0]],
        rows=10,
        description="Options",
        disabled=False,
    )
    return widg


class Selector(object):
    """Coordinates interaction with dropdown widget to make simple vocabularies.

    Options are filtered by a regular expression written to reflect the include and exclude inputs, and these are updated when changed and shown in the dropdown. The user should select using `command` or `control` to make multiple options. Then push the "save" button when the nickname and selected options from the dropdown menu are the variables you want to include exactly in a future regular expression search.

    Examples
    --------

    Show widget with a short list of options. Input a nickname and press button to save an entry to the running vocabulary in the object:

    >>> import cf_pandas as cpf
    >>> sel = cfp.Selector(options=["var1", "var2", "var3"])
    >>> display(sel.button_save)
    >>> sel.output

    See resulting vocabulary with:

    >>> sel.vocab
    """

    def __init__(
        self,
        options: Sequence,
        vocab: Optional[Vocab] = None,
        nickname_in: str = "",
    ):
        """Initialize Selector object.

        Parameters
        ----------
        options: Sequence
            strings to select from in the dropdown widget. Will be filtered by include and exclude  inputs.
        vocab: Vocab object
            Defaults to None. A vocabulary will be created as part of using this widget. However, instead a vocabulary can be input via this argument and then will be amended with the entries made with the widget.
        """

        # create an output widget in order to show output instead of going to log
        self.output = widgets.Output()

        if vocab is None:
            self.vocab = Vocab()
        else:
            self.vocab = vocab

        self.dropdown_values: Sequence = []
        self.include = ""
        self.exclude = ""

        self.button_save = widgets.Button(description="Press to save")

        self.nickname_text = widgets.Text(value=nickname_in)
        self.nickname = self.nickname_text.value

        self.dropdown = widgets.interact(
            dropdown,
            options=widgets.fixed(options),
            nickname=self.nickname,
            include=self.include,
            exclude=self.exclude,
        )

        self.button_save.on_click(self.button_pressed)

    def button_pressed(self, *args):
        """Saves a new entry in the catalog when button is pressed."""

        # print vocab
        # clear the output on every click of randomize self.val
        self.output.clear_output()

        # execute function so it gets captured in output widget view
        with self.output:
            if self.dropdown.widget.kwargs["nickname"] == "":
                raise KeyError("Must input nickname to make entry.")

            # regular expressions to put into entries: exact matching
            res = [
                Reg(include_exact=exp).pattern()
                for exp in self.dropdown.widget.result.value
            ]
            self.vocab.make_entry(
                self.dropdown.widget.kwargs["nickname"], res, attr="standard_name"
            )
            print(self.vocab.vocab)
