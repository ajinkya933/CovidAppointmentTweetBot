import datetime
import hashlib
import json
import pickle
import time

import requests
import tweepy

from beepy import beep
from requests import ReadTimeout, Timeout

from multiprocessing import Pool

# Global variables therefore loading them here

# Cities
# Schema
# {
#     "city_name": [
#         {
#             "id": district_id,
#             "district": "district_name"
#         },
#     ],
# }

# Example
# {
#     "Chennai": [
#         {
#             "id": 571,
#             "district": "Chennai"
#         },
#         {
#             "id": 575,
#             "district": "Poonamallee"
#         }
#     ],
# }
print("Loading cities")
with open('cities.json', 'rb') as cities_file:
    cities = json.load(cities_file)
print("Loading cities complete")

# Access tokens for each bot
# Schema
# {
#     "city_name": {
#         "access_token": "twitter access token for the bot account",
#         "access_token_secret": "twitter access token secret for the bot account"
#     },
# }
print("Loading access tokens")
with open('access_tokens.json', 'rb') as access_token_file:
    access_tokens = json.load(access_token_file)
print("Loading access tokens complete")

# Twitter developer keys
# Schema
# {
#   "consumer_key": "twitter consumer key",
#   "consumer_secret": "twitter consumer key secret"
# }
print("Loading twitter tokens")
with open('twitter_oauth.json', 'rb') as twitter_token_file:
    twitter_tokens = json.load(twitter_token_file)
print("Loading twitter tokens complete")


# makes beep sound number_of_beeps times
def make_noise(number_of_beeps):
    for i in range(number_of_beeps):
        beep(sound=3)


# sleeps for duration_int
def sleep_time(duration_int):
    print("Sleeping for", duration_int, "seconds")
    for i in range(duration_int):
        print("Elapsed time", str(i + 1) + "s")
        time.sleep(1)


def city(city_to_tweet):
    session = requests.Session()
    init_url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict"
    date = datetime.date.today()

    print('Loading file ' + city_to_tweet + ".data")

    try:
        with open(city_to_tweet + '.data', 'rb') as availability_checked_file:
            already_checked_hash_list = pickle.load(availability_checked_file)
    except FileNotFoundError:
        already_checked_hash_list = set()

    auth = tweepy.OAuthHandler(twitter_tokens['consumer_key'], twitter_tokens['consumer_secret'])
    auth.set_access_token(access_tokens[city_to_tweet]['access_token'],
                          access_tokens[city_to_tweet]['access_token_secret'])

    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    for districts in cities[city_to_tweet]:
        for i in range(0, 7):
            print("Fetching " + districts['district'] + " " + str(i + 1) + "/7")
            date_to_fetch = date + datetime.timedelta(days=i)
            completed_url = init_url + "?" + "district_id=" + str(districts['id']) + "&" + "date=" + str(
                date_to_fetch.day) + "-" + str(date_to_fetch.month) + "-" + str(date_to_fetch.year) + ""
            try:
                data = session.get(completed_url).json()
            except (ReadTimeout, Timeout, ConnectionError) as e:
                print(e)
                make_noise(20)
                continue
            centers = data['centers']
            if len(centers) <= 0:
                continue
            for c in centers:
                sessions = c['sessions']
                eighteen_plus_and_cap = False
                for s in sessions:
                    min_age_limit = s['min_age_limit']
                    available_capacity = s['available_capacity']
                    if min_age_limit < 45 and available_capacity > 0:
                        eighteen_plus_and_cap = True
                if eighteen_plus_and_cap:
                    hash_str = c['state_name'].replace(" ", "") + c['district_name'].replace(" ", "") + c['name'] + str(
                        date_to_fetch.day) + "/" + str(date_to_fetch.month)
                    hash_val = hashlib.md5(hash_str.encode('utf-8')).hexdigest()
                    if hash_val not in already_checked_hash_list:
                        tweet = "#Vaccine appointment available for ages 18 and above in #" + c[
                            'state_name'].replace(" ", "") + ", #" + c['district_name'].replace(
                            " ", "") + " at " + \
                                c['name'] + "(" + str(c['pincode']) + ")" + " on " + str(date_to_fetch.day) + "/" + str(
                            date_to_fetch.month) + " #COVID19 #CovidIndia"
                        print("Tweeting " + tweet)
                        sleep_time(2)
                        api.update_status(tweet)
                        already_checked_hash_list.add(hash_val)
            sleep_time(1)

    print("Writing file " + city_to_tweet + ".data")
    with open(city_to_tweet + '.data', 'wb') as availability_checked_file:
        pickle.dump(already_checked_hash_list, availability_checked_file)


def city_loop(city_name):
    while True:
        city(city_name)


def main():
    c = cities.keys()
    with Pool(len(c)) as p:
        p.map(city_loop, c)


if __name__ == '__main__':
    main()
