import json
import os.path
import pathlib
import time
from bisect import bisect
from shutil import move

from requests import Timeout
from tenacity import stop_after_attempt, wait_exponential, retry_if_exception_type

from utils import twitter, Parser, setup_logger

STOP = stop_after_attempt(5)
WAIT = wait_exponential(multiplier=1, min=30, max=900)
RETRY = retry_if_exception_type(Timeout)

logger = setup_logger()


def save_following(user, following, outdir):
    pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)

    out = sorted([f"{u['id']},{u['screen_name']},following\n" for u in following])
    csv = f'@{user}.csv'

    path = os.path.join(outdir, csv)
    path_tmp = path + '.tmp'

    path_bkup_dir = os.path.join(outdir, 'backup')
    pathlib.Path(path_bkup_dir).mkdir(parents=True, exist_ok=True)
    path_bkup = os.path.join(path_bkup_dir, f'@{user}-{time.strftime("%Y%m%d%H%M%S")}.csv')

    def split(line):
        l = line.split(',')
        l[0] = int(l[0])
        return l

    # Check for unfollowed users
    if os.path.exists(path):
        with open(path, 'r') as file:
            old_following = [dict(zip(['id', 'screen_name', 'status'],
                                      split(line))) for line in file.read().splitlines()[1:]]

        # for u in [f for f in old_following if not any(f['id'] == o['id'] for o in following)]
        # ^compares by just id, will lead to old screen names not being saved
        for u in [f for f in old_following if not any(f.items() >= o.items() for o in following)]:
            s = f"{u['id']},{u['screen_name']},unfollowed\n"
            i = bisect(out, s)
            out[i:i] = [s]

        # backup old csv
        move(path, path_bkup)

    # Write to temp file
    with open(path_tmp, 'w') as file:
        file.write('screen_name, id, status\n')
        file.writelines(out)

    # Overwrite real file
    move(path_tmp, path)


def parse_arguments():
    parser = Parser(usage="%(prog)s {USERS, FILE}... [OPTION]...")
    parser.add_argument('input', nargs='+', help='Users or input file')
    parser.add_argument('-o', nargs='?', type=pathlib.Path, metavar='FOLDER', help='Output folder')
    parser.add_argument('-auth', nargs='?', type=pathlib.Path, metavar='auth.json', help='Auth config file')
    args = parser.parse_args()

    users = []
    for input in args.input:
        if os.path.exists(input):
            with open(input) as file:
                users.extend(file.read().splitlines())
        else:
            users.append(input)

    outdir = os.path.abspath(args.o if args.o else 'out')

    auth_path = os.path.abspath(args.auth if args.auth else 'auth.json')
    with open(auth_path) as file:
        auth_info = json.load(file)

    return users, outdir, auth_info


def main():
    users, outdir, auth_info = parse_arguments()
    for user in users:
        logger.info(f"Tracking @{user}...")
        try:
            save_following(user, twitter.API(auth_info).get_friends(user), outdir)
        except Exception as e:
            logger.error(e)


if __name__ == "__main__":
    main()
