import requests
import json
from xml.etree import ElementTree
from tkinter.font import *
import http.client

headers = {
    "x-nxopen-api-key": "test_1afb40fe1643062715cabee53b8c4aa9876c94ce1f82999c2f4ad21e3937c6deefe8d04e6d233bd35cf2fabdeb93fb0d"
}

def get_ouid(character_name):
    userouidURL = "https://open.api.nexon.com/fconline/v1/id?nickname=" + character_name
    response = requests.get(userouidURL, headers=headers)
    response_json = response.json()
    return response_json.get('ouid')

def get_user_info(ouid):
    userinfoURL = 'https://open.api.nexon.com/fconline/v1/user/basic?ouid=' + ouid
    response = requests.get(userinfoURL, headers=headers)
    response_json = response.json()
    return response_json.get('nickname'), response_json.get('level')

def get_match_ids(ouid, matchtype='50', offset='0', limit='20'):
    usermatchURL = ('https://open.api.nexon.com/fconline/v1/user/match?ouid=' + ouid +
                    '&matchtype=' + matchtype + '&offset=' + offset + '&limit=' + limit)
    response = requests.get(usermatchURL, headers=headers)
    return response.json()

def get_match_details(match_ids):
    match_details = []
    for matchid in match_ids:
        userdetailinfoURL = 'https://open.api.nexon.com/fconline/v1/match-detail?matchid=' + matchid
        response = requests.get(userdetailinfoURL, headers=headers)
        match_detail = response.json()
        match_details.append(match_detail)
    return match_details

def print_other_player_nicknames(match_details, main_nickname):
    for match_detail in match_details:
        for match_info in match_detail.get('matchInfo', []):
            if match_info.get('nickname') != main_nickname:
                player_nickname = match_info.get('nickname')
                print(f"Match ID: {match_detail['matchId']}, Player Nickname: {player_nickname}")

def main(character_name):
    ouid = get_ouid(character_name)
    nickname, level = get_user_info(ouid)
    print(f"ouid: {ouid}")
    print(f"nickname: {nickname}, level: {level}")

    match_ids = get_match_ids(ouid)
    match_details = get_match_details(match_ids)

    print_other_player_nicknames(match_details, nickname)

if __name__ == "__main__":
    character_name = "극지고"
    main(character_name)