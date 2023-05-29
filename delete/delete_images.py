from pathlib import Path

from send2trash import send2trash

from utils import Parser, setup_logger

logger = setup_logger()


def delete_images(dir_):
    for file in list(Path(dir_).rglob("[*.*")):
        logger.info(f"Trashing: {file}")
        send2trash(file)


def parse_arguments():
    parser = Parser(usage="%(prog)s {DIR}")
    parser.add_argument('dir', help='Source directory')
    args = parser.parse_args()
    return args.dir


def main():
    dir_ = parse_arguments()
    delete_images(dir_)


if __name__ == "__main__":
    main()
