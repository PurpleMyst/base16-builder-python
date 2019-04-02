import sys

from . import updater, builder, colorparser


def main():
    updater.update()
    scheme = colorparser.generate_colorscheme(sys.argv[1])
    builder.build(scheme)


if __name__ == "__main__":
    main()
