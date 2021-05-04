import json
import pickle

import requests

init_url = "https://cdn-api.co-vin.in/api"

states_url = init_url + "/v2/admin/location/states"
districts_url = init_url + "/v2/admin/location/districts/"

data = {}

session = requests.Session()

states = session.get(states_url).json()["states"]

for state in states:
    state_name = state["state_name"]
    state_id = state["state_id"]
    dist_data = []
    districts_url_c = districts_url + str(state_id)
    # print(districts_url_c)
    districts = session.get(districts_url_c).json()["districts"]
    # return
    for district in districts:
        district_id = district["district_id"]
        district_name = district["district_name"]
        temp_d_data = {
            "id": district_id,
            "district": district_name
        }
        dist_data.append(temp_d_data)
    data[state_name] = dist_data

with open('data.json', 'w', encoding='utf-8') as data_file:
    json.dump(data, data_file)
