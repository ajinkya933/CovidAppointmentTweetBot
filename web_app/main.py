import datetime
import hashlib
import json
import pickle
import time
import requests
from requests import ReadTimeout, Timeout
from multiprocessing import Pool
import sys
# import streamlit as st
# st.write('hello')
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
city=sys.argv[1]

print("Loading cities")
with open(str(city) +'.json', 'rb') as cities_file:
    cities = json.load(cities_file)
print("Loading cities complete")

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

    # auth = tweepy.OAuthHandler(twitter_tokens['consumer_key'], twitter_tokens['consumer_secret'])
    # auth.set_access_token(access_tokens[city_to_tweet]['access_token'],
    #                       access_tokens[city_to_tweet]['access_token_secret'])

    # api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

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
                # make_noise(20)
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
                    if min_age_limit < 40 and available_capacity > 0:
                        eighteen_plus_and_cap = True
                if eighteen_plus_and_cap:
                    hash_str = c['state_name'].replace(" ", "") + c['district_name'].replace(" ", "") + c['name'] + str(
                        date_to_fetch.day) + "/" + str(date_to_fetch.month)
                    hash_val = hashlib.md5(hash_str.encode('utf-8')).hexdigest()
                    if hash_val not in already_checked_hash_list:
                        tweet = c[
                            'state_name'].replace(" ", "") + ", #" + c['district_name'].replace(
                            " ", "") + " at " + \
                                c['name'] + "(" + str(c['pincode']) + ")" + " on " + str(date_to_fetch.day) + "/" + str(
                            date_to_fetch.month)
                        print("Tweeting " + tweet)
                        with open('Pune_list.csv','a') as fd:
                           fd.write(tweet)

                        
                        sleep_time(10)
                        # api.update_status(tweet)
                        already_checked_hash_list.add(hash_val)
            sleep_time(5)
            # st.write(tweet)

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

