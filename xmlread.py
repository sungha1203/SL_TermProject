import os
from tkinter import *
from tkinter.ttk import *
from tkinter.ttk import *
import requests
import json
from xml.etree import ElementTree
from tkinter.font import *
import http.client
headers = {
    "x-nxopen-api-key": "test_1afb40fe1643062715cabee53b8c4aa9876c94ce1f82999c2f4ad21e3937c6deefe8d04e6d233bd35cf2fabdeb93fb0d"
}

characterName = "극지고"

userouidURL = "https://open.api.nexon.com/fconline/v1/id?nickname=" + characterName
response = requests.get(userouidURL, headers=headers)



response_json = response.json()
ouid = response_json.get('ouid')

#https://open.api.nexon.com/fconline/v1/user/basic?ouid
userinfoURL = 'https://open.api.nexon.com/fconline/v1/user/basic?ouid=' + ouid

response = requests.get(userinfoURL, headers=headers)
response_json = response.json()
nickname = response_json.get('nickname')
level = response_json.get('level')


print(ouid)
print(nickname,level)
matchtype = '50'    #공식경기 매치타입
offset = '0'
limit = '20'
usermatchURL = ('https://open.api.nexon.com/fconline/v1/user/match?ouid=' + ouid +
                '&matchtype='+matchtype+'&offset='+offset+'&limit='+limit)

response = requests.get(usermatchURL, headers=headers)
matches = response.json()
#serdetailinfoURL = 'https://open.api.nexon.com/fconline/v1/match-detail?matchid=' + matchid
match_details = []
for matchid in matches:
    userdetailinfoURL = 'https://open.api.nexon.com/fconline/v1/match-detail?matchid=' + matchid
    response = requests.get(userdetailinfoURL, headers=headers)
    match_detail = response.json()
    match_details.append(match_detail)

    for match_info in match_detail.get('matchInfo', []):
        if match_info.get('nickname') != nickname:
            player_nickname = match_info.get('nickname')
            print(f"Match ID: {matchid}, Player Nickname: {player_nickname}")