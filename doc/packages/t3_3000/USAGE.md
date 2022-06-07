# Usage

To use this package, add the folder to your `TEXINPUTS` and your `BIBINPUTS` environment variables.

If you are using latexmk, just add
```perl
ensure_path('TEXINPUTS','path/to/t3_3000');
ensure_path('BIBINPUTS','path/to/t3_3000');
```
to your `.latexmkrc`.

Then you use the documentclass in your `tex`-file as follows:
```LaTeX
\documentclass[
]{t3_3000}


\begin{document}

\maketitle

\end{document}
```

An example document is provided as `t3_3000.tex`.
