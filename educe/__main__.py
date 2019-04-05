import sys

from . import updater, builder, colorparser


def main():
    if sys.argv[1] == "update":
        updater.update()
    elif sys.argv[1] == "build":
        scheme = colorparser.generate_colorscheme(sys.argv[2])
        builder.build(scheme)
    else:
        raise RuntimeError("no command given")


if __name__ == "__main__":
    main()
