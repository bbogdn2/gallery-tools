import re
from os import listdir, makedirs, error
from os.path import isfile, join
from pathlib import Path
from shutil import move

from utils import Parser, setup_logger

logger = setup_logger()


def rename_images_twitter(dir_):
    for file in list(Path(dir_).rglob("[*.*")):
        try:
            # Rename parameters
            file_str = file.__str__()
            y = re.findall(r'\[(\d{4})-[\-\d]*\]', file_str)[0]
            new_file = Path(file_str.replace(y, y[2:]))
        except:
            continue
        logger.info(f"[Rename] {file} -> {new_file}".encode('utf-8'))
        move(file, new_file)


def rename_images_twitter_retweets_old(dir_):
    for filename in [f for f in listdir(dir_) if isfile(join(dir_, f))]:
        username, tweet_id, date, num, ext = \
            re.findall(r'([^-]+)-([^-]+)-([^-_]+)_[^-]+-(?:img|vid|gif)([^\.])\.(.+)', filename)[0]
        artist_dir = '(@' + username + ')'
        new_filename = '[' + date[:4] + '-' + date[4:6] + '-' + date[6:] + '] ' + tweet_id + '_p' + str(
            int(num) - 1) + '.' + ext
        dest_dir = join(dir_, artist_dir)

        try:
            makedirs(dest_dir)
        except error as e:
            pass

        move(join(dir_, filename), join(dest_dir, new_filename))


def rename_images_weibo(dir_):
    for file in list(Path(dir_).rglob("*.*")):
        try:
            # Rename parameters
            file_str = file.__str__()
            y = re.findall(r'_p[\d]+', file_str)[0]
            new_file = Path(file_str.replace(y, ''))
        except:
            continue
        logger.info(f"[Rename] {file} -> {new_file}".encode('utf-8'))
        move(file, new_file.__str__())


def parse_arguments():
    parser = Parser(usage="%(prog)s {DIR}")
    parser.add_argument('dir', help='Source directory')
    args = parser.parse_args()
    return args.dir


def main():
    dir_ = parse_arguments()
    rename_images_twitter(dir_)


if __name__ == "__main__":
    main()
