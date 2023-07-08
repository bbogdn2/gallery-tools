import re
from os import listdir

import tweepy

from utils import setup_logger, paginate

RETRY_COUNT = 5
PAGE_SIZE = 100


class API:
    def __init__(self, auth_info, outdir):
        self.api = self.__get_api(auth_info, RETRY_COUNT)
        setup_logger(outdir)

    def lookup_users(self, user_ids_list=None, screen_names_list=None, page_size=PAGE_SIZE):
        errors, users = [], []

        # Lookup users by ids
        for user_ids in paginate(user_ids_list, page_size):
            users.extend(self.__lookup_users(user_id=user_ids))

        # Lookup users by screen_names
        for screen_names in paginate(screen_names_list, page_size):
            try:
                users.extend(self.__lookup_users(screen_name=screen_names))
            except:
                errors.extend(screen_names)

        return users, errors

    def lookup_statuses(self, ids_list, page_size=PAGE_SIZE):
        statuses = []
        for ids in paginate(ids_list, page_size):
            statuses.extend(self.__lookup_statuses(id=ids))
        return statuses

    def get_friends(self, screen_name):
        friend_ids_list = self.__get_friend_ids(screen_name=screen_name)
        friends_list, _ = self.lookup_users(user_ids_list=friend_ids_list)
        return [dict({'screen_name': u.screen_name, 'id': u.id}) for u in friends_list]

    @classmethod
    def __get_api(cls, auth_info, retry_count=0):
        auth = tweepy.OAuthHandler(auth_info['consumer_key'], auth_info['consumer_secret'])
        auth.set_access_token(auth_info['access_token'], auth_info['access_token_secret'])
        return tweepy.API(auth, retry_count=retry_count, retry_errors=[408, 425, 429,
                                                                       500, 502, 503, 504],
                          wait_on_rate_limit=True)

    def __lookup_users(self, *args, **kwargs):
        return list(self.api.lookup_users(*args, **kwargs))

    def __lookup_statuses(self, *args, **kwargs):
        return self.api.lookup_statuses(*args, **kwargs)

    def __get_friend_ids(self, *args, **kwargs):
        return list(tweepy.Cursor(self.api.get_friend_ids, *args, **kwargs).items())


class CLIENT:
    def __init__(self, auth_info, outdir):
        self.client = self.__get_client(auth_info)
        setup_logger(outdir)

    @classmethod
    def __get_client(cls, auth_info):
        return tweepy.Client(bearer_token=auth_info['bearer_token'],
                             consumer_key=auth_info['consumer_key'],
                             consumer_secret=auth_info['consumer_secret'],
                             access_token=auth_info['access_token'],
                             access_token_secret=auth_info['access_token_secret'],
                             wait_on_rate_limit=True)

    def get_tweets(self, ids_list, page_size=PAGE_SIZE):
        tweets = []
        for ids in paginate(ids_list, page_size):
            tweets.extend(self.client.get_tweets(ids=ids))
        return tweets

    def get_users(self, user_ids_list=None, screen_names_list=None, page_size=PAGE_SIZE):
        users, errors = [], []

        for user_ids in paginate(user_ids_list, page_size):
            users.extend(self.client.get_users(user_id=user_ids))

        for screen_names in paginate(screen_names_list, page_size):
            # TODO DEBUG
            batch = self.client.get_users(usernames=screen_names)
            users.extend(batch)

        return users, errors

    def get_following(self, screen_name=None, user_id=None):
        if (screen_name and user_id) or not (screen_name or user_id):
            raise Exception('Must only take one argument, either screen_name or user_id')

        # TODO DEBUG
        if screen_name:
            user_id = self.client.get_me(username=screen_name).id
        return tweepy.Paginator(self.client.get_users_following, id=user_id).flatten()


def get_screen_names(str):
    match = re.findall(r'\(@([a-zA-Z\d_]+)\)?$|^([a-zA-Z\d_]+)?(?: \(twitter_\d+\))?$', str)
    return next(m for m in match[0] if m)


def get_screen_names_by_directory(dir_):
    return [get_screen_names(d) for d in listdir(dir_)]
