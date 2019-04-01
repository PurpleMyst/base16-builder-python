from termcolor import cprint

from . import updater, builder, colorparser


def main():
    updater.update()

    print()

    scheme = colorparser.generate_colorscheme("img.jpg")

    print()

    builder.build(scheme)


if __name__ == "__main__":
    main()
