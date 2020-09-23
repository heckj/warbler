# Warbler

This is a [language server] implementation for markdown, specifically focusing
on using the LSP to provide writer feedback for content, rather than concrete validation of the markdown structure to any specification.

[language server]: https://langserver.org/

This is an experimental implementation, intended to leverage modern NLP systems to identify and highlight the use of passive in written content.

Code for the LSP python implementation is derived from [Benten](https://github.com/rabix/benten) - another LSP that's implemented in python.

The name was chosen as a [common small songbird](http://www.pacificnorthwestbirds.com/category/warbler-summer/) from the pacific northwest. Something to look over your shoulder and call out...

## Dev Notes

This setup uses tox for most of it's build and such, so you'll need it as a prerequisite. 
If you don't already have it installed:

    pip3 install tox

Run tests:

    tox

Development work:

- activate the tox generated virtual environment:

    source .tox/py38/bin/activate
    pip3 install .

- use your the editor happily

    code .

- run stand-alone on the CLI

    python warbler

- local virtualenv outside of .tox

    python3 -m venv .venv
    python3 -m pip install --upgrade pip
    source .venv/bin/activate
    pip3 install .
