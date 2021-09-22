# Packages Repo

This repository contains packages written to make tasks easier.

Add them via

```sh
git remote add URL REMOTE
git subtree add -p packages/ REMOTE main
```

To use them add the following lines to your `.latexmkrc` for each package:

```perl
ensure_path( 'TEXINPUTS', './packages/PACKAGE_NAME/' ); # find the sty and tex files
ensure_path( 'BIBINPUTS', './packages/PACKAGE_NAME/' ); # find the bib files
```
