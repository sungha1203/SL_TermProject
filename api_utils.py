import requests
import xml.etree.ElementTree as ET

headers = {
    "x-nxopen-api-key": "test_a1117976d21f0e110832cec871e43bd95a8b6510b740e366a06718fec6508af6efe8d04e6d233bd35cf2fabdeb93fb0d"
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


def get_match_ids(ouid, matchtype='50', offset='0', limit='10'):
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


def get_maxdivision(ouid):
    MaxDivisionURL = 'https://open.api.nexon.com/fconline/v1/user/maxdivision?ouid=' + ouid
    response = requests.get(MaxDivisionURL, headers=headers)
    response_json = response.json()

    if isinstance(response_json, list) and len(response_json) > 0:
        return response_json[0].get('division')
    else:
        return None


def get_spid_metadata():
    url = "https://open.api.nexon.com/static/fconline/meta/spid.json"
    response = requests.get(url)
    return response.json()


def get_division_data():
    url = "https://open.api.nexon.com/static/fconline/meta/division.json"
    response = requests.get(url)
    return response.json()


def get_season_metadata():
    url = "https://open.api.nexon.com/static/fconline/meta/seasonid.json"
    response = requests.get(url)
    return response.json()


def fetch_data(sigun_nm):
    api_url = "https://openapi.gg.go.kr/GameSoftwaresFacilityProvis"
    api_key = "9c52941f1f09418cb908e5388454c307"

    params = {
        "KEY": api_key,
        "Type": "xml",
        "pIndex": 1,
        "pSize": 1000,
        "SIGUN_NM": sigun_nm,
    }

    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        items = root.findall(".//row")
        result = []
        for item in items:
            if item.findtext("BSN_STATE_NM") == "운영중":
                name = item.findtext("BIZPLC_NM")
                address = item.findtext("REFINE_ROADNM_ADDR")
                lat = item.findtext("REFINE_WGS84_LAT")
                lng = item.findtext("REFINE_WGS84_LOGT")
                result.append((name, address, lat, lng))
        return result
    else:
        return []