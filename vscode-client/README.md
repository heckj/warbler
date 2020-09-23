# VS Code plugin for Rabix/Benten CWL language server

<!-- <img height="400px" src="https://raw.githubusercontent.com/rabix/benten/master/media/2019.12.03/full-window.png"></img> -->

- Syntax highlighting (Use of Passive Voice)

## Server installation

This plugin requires the [Warbler Language Server](https://github.com/heckj/warbler) to be installed.

**If you install the server after loading a markdown file you will have to
restart VS Code.**

**If you are trying to reinstall or upgrade the server on windows with
VS Code running, you will have to exit VS Code, since it will be running
the server and will have locked it from changes.**

## Using pipx

A neat way to install `warbler` in a virtual env (isolating it from your
system python) and still be able to call it as a regular executable is
to use `pipx`

```
pip3 install pipx  # in case you don't have pipx
pipx ensurepath # ensures CLI application directory is on your $PATH
pipx upgrade warbler
```

For more detailed information please see the [project page](https://github.com/heckj/warbler).

<div align="right">
<sub>(c) 2020 Joseph Heck</sub>
</div>
