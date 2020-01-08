from argparse import ArgumentParser


def main():

    parser = ArgumentParser(prog="tm listuids")
    parser.add_argument("conf_file", help="The configuration file")

    args = parser.parse_args()

    conf_file = {}
    with open(args.conf_file, "r") as inf:
        exec(inf.read(), conf_file)
    for UID, info in list(conf_file["REGISTERED_UIDS"].items()):
        print("{}\t{}".format(UID, info))


if __name__ == "__main__":
    main()
