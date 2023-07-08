import __main__
import argparse
import logging
import pathlib
import sys
import time
from os.path import splitext, basename


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_help()
        sys.exit(2)


def setup_logger():
    base_py = basename(__main__.__file__)
    base = splitext(base_py)[0]
    logging.basicConfig(format="[%(name)s][%(levelname)s] %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                        level=logging.INFO,
                        handlers=[
                            logging.FileHandler(f"{pathlib.Path(base).stem}_{time.strftime('%Y%m%d%H%M%S')}.log"),
                            logging.StreamHandler()
                        ])
    return logging.getLogger(base_py)


def paginate(collection, n):
    if not collection:
        return None
    for a in range(0, len(collection), n):
        yield collection[a:a + n]
