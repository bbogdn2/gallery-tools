import json
import os
from datetime import datetime

from utils import setup_logger, Parser

logging = setup_logger()


def fix_tasks(in_path):
    out_path = os.path.splitext(in_path)[0] + '_(' + str(datetime.now().date()) + ')_restart.hdt'

    # Get data
    with open(in_path) as file:
        data = json.load(file)

    for entry in data[1:]:
        entry['valid'] = True
        entry['label_color'] = None
        entry['done'] = False

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
