import os
import re
from shutil import move

from utils import Parser, setup_logger

logger = setup_logger()


def undo_rename(logfile, dir_):
    with open(logfile) as file:
        for line in file.readlines():
            src, dst = map(lambda x: os.path.join(dir_, x), re.findall(r'\[Rename\] (.+) -> (.+)$', line)[0])
            if not os.path.isdir(dst):
                continue
            move(dst, src)
            logger.info(f'[Rename] {dst.split(os.sep)[-1]} -> {src.split(os.sep)[-1]}')


def parse_arguments():
    parser = Parser(usage="%(prog)s {LOGFILE} {DIR}")
    parser.add_argument('logfile', help='Log file')
    parser.add_argument('dir', help='Source directory')
    args = parser.parse_args()
    return args.logfile, args.dir


def main():
    logfile, dir_ = parse_arguments()
    undo_rename(logfile, dir_)


if __name__ == "__main__":
    main()
