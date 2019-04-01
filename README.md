educe
=====

`educe` is a program to let you generate a colorscheme from an image.

Usage
-----

Run the script this way:

    python3 -m educe IMAGE

This will:

1. Download all Base16 templates to `sources/templates/`
2. Extract the 16 main colors from the image passed as argument.
3. Build all Base16 templates with the image palette in `output/`.

Thanks
------

Thanks to InspectorMustache for the original repo of
`base16-builder-python`, which this repo is based on.

Thanks also to [coleifer](https://github.com/coleifer) for
[themer](https://gist.github.com/coleifer/33484bff21c34644dae1), which gave me
the code for the K-Means palette extraction.
