import requests
import os
from JellyFin import Client
import logging

client = Client.JellyfinClient()

client.set_user("d9871f7d73ff45e797770cf6436c397b")

client.get_played()

# url = "https://jf.vicinusvetus.nl/Items?userId=d9871f7d73ff45e797770cf6436c397b&filters=IsPlayed&recursive=true&sortBy=DatePlayed"

# payload = {}
# headers = {
#   'Accept': 'application/json',
#   'Authorization': 'MediaBrowser Token="73d32c0da8714673904793326880348b"'
# }

# response = requests.request("GET", url, headers=headers, data=payload)

# data = response.json()['Items']

# movies = filter(lambda obj: obj['Type'] == 'Movie', data)

# for (i, obj) in enumerate(movies):
#     print(f'Currently at item [{obj["Name"]}]')



#     url = f"https://jf.vicinusvetus.nl/Users/d9871f7d73ff45e797770cf6436c397b/Items/{obj['Id']}"

#     req2 = requests.request("GET", url, headers=headers)


#     print(req2.json()['Path'])
#     print("")

#     print(os.path.exists(req2.json()['Path']))