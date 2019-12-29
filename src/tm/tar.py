from argparse import ArgumentParser

from tm.client import tar


def main():

    parser = ArgumentParser(prog="tm tar")
    parser.add_argument("--dir", "-d", default=".", help="The dir to act on")
    parser.add_argument("--glob", "-g", default=".*", help="The glob to use to filter files")

    args = parser.parse_args()

    tar(args.dir, args.glob, True)

if __name__ == "__main__":
    main()
