import sys

from . import updater, builder, colorparser


def main():
    updater.update()

    print()

    scheme = colorparser.generate_colorscheme(sys.argv[1])

    print()

    builder.build(scheme)


if __name__ == "__main__":
    main()
