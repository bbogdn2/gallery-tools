import json
import os
import re
from datetime import datetime
from os import listdir

from utils import setup_logger, Parser

logging = setup_logger()


def fix_tasks(in_path):
    out_path = os.path.splitext(in_path)[0] + '_(' + str(datetime.now().date()) + ')_new.hdt'

    # Get data
    with open(in_path) as file:
        data = json.load(file)

    hitomi_dirs = listdir(r'E:\collection\dls\hitomi-dl\hitomi_downloaded_twitter')

    for entry in data[1:]:
        dir_ = entry['dir']

        if entry['type'] == 'twitter':
            result = re.findall(r"\(@(.*)\)$", dir_)
            if len(result) == 0:
                logging.info(f'[Skipped] {dir_}')
                continue
            username = result[0]

            new_dir = 'hitomi_downloaded_twitter\\'
            try:
                new_dir += next(d for d in hitomi_dirs if username.lower() in d.lower())
            except StopIteration:
                logging.info(f'[Failed] {dir_} ')
                continue

            new_username = re.findall(r"[/\\]([^\s]+)[^/\\]+$", new_dir)[0]
            new_url = f'https://twitter.com/{new_username}'

            entry['dir'] = new_dir
            entry['gal_num'] = new_url
            entry['url'] = new_url

            logging.info(f'[Changed] {dir_} -> {new_dir}')

    with open(out_path, 'w') as file:
        file.write(json.dumps(data))


def parse_arguments():
    parser = Parser(usage="%(prog)s {FILE}")
    parser.add_argument('file', help='File')
    args = parser.parse_args()
    return args.file


def main():
    setup_logger()
    file = parse_arguments()
    fix_tasks(file)


if __name__ == "__main__":
    main()
