
To get started pip install Sphinx:

`pip install -U sphinx`

Edit *.rst files with the *source* directory to add functions and classes to the documentation. Additional documentation can be added directly to the .rst files using Markdown syntax.

The Sphinx configuration file is *conf.py*. Currently the configuration is set to autoparse Numpy and Google style docstrings using sphinx.ext.napoleon

To build new html enter the docs directory and type in a terminal:
`make html`

The resulting output while be found in the *build* directory. The root is *index.html* 
