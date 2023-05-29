import json
import os
import pathlib
import re
from os import listdir
from shutil import move

from tweepy import User

from utils import Parser, twitter, setup_logger, paginate
from utils.twitter import get_screen_names_by_directory

logger = setup_logger()


def get_ids(dir_):
    return [re.findall(r'\(twitter_(\d+)\)', d)[0] or None for d in listdir(dir_)]


def rename(dir_: str, user: User):
    src = os.path.join(dir_, next(d for d in listdir(dir_) if user.screen_name in d))
    dst = os.path.join(dir_, f"{user.screen_name} (twitter_{user.id})")
    if src != dst:
        move(src, dst)
        logger.info(f"[Rename] {src.split(os.sep)[-1]} -> {dst.split(os.sep)[-1]}")


def rename_twitter_folders(API, dir_):
    users, errors = API.lookup_users(screen_names_list=get_screen_names_by_directory(dir_))

    # Rename successful lookups
    for user in users:
        rename(dir_, user)

    # Try fallback for errors
    for screen_name in errors:

        result = [re.findall('\[.*\] (\d+)_p\d.*', d)
                  for d in listdir(next(os.path.join(dir_, e)
                                        for e in listdir(dir_)
                                        if screen_name in e))]

        ids_list = [r[0] for r in result if r]

        # Find user via status lookups
        if not ids_list:
            logger.error(f"[Failed] @{screen_name} doesn't exist")
            continue
        else:
            for ids in paginate(ids_list, 100):
                request = API.lookup_statuses(ids_list=ids)
                if request:
                    user = API.lookup_statuses(ids_list=ids)[0].user
                    break
            else:
                logger.error(f"[Failed] @{screen_name} doesn't exist")
                continue

            # Rename successful lookups
            rename(dir_, user)


def parse_arguments():
    parser = Parser(usage="%(prog)s {DIR} [OPTION]...")
    parser.add_argument('dir', help='Source directory')
    parser.add_argument('-auth', nargs='?', type=pathlib.Path, metavar='auth.json', help='Auth config file')
    args = parser.parse_args()

    auth_path = os.path.abspath(args.auth if args.auth else 'auth.json')
    with open(auth_path) as file:
        auth_info = json.load(file)

    return args.dir, auth_info


def main():
    dir_, auth_info = parse_arguments()
    rename_twitter_folders(twitter.API(auth_info), dir_)


if __name__ == "__main__":
    main()
