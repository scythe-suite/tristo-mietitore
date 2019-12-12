from argparse import ArgumentParser

from tm.client import untar


def main():

    parser = ArgumentParser(prog="tm untarconf")
    parser.add_argument("conf_file", help="The configuration file")
    parser.add_argument("output_dir", help="The directory where to extract TAR_DATA")

    args = parser.parse_args()

    conf_file = {}
    with open(args.conf_file, "r") as inf:
        exec(inf, conf_file)
    tar_data = conf_file["TAR_DATA"]
    untar(tar_data, args.output_dir)

if __name__ == "__main__":
    main()
