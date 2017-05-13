import datetime
import requests
import simplejson as json
CLIENT_ID = 'e562c31c-8d56-4696-858c-9331c21688d4'
CLIENT_SECRET = 'mYvtKREFRbA4zANzs1NQuGvLQmgOhmvJDpEl6kiu/cQ='
PLATFORM_API_URL = 'https://platform.whereismytransport.com/api'

WIMT_TOKEN = ''

def getAccessToken():
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
        "scope": "transportapi:all"
    }

    r = requests.post( 'https://identity.whereismytransport.com/connect/token', data=payload)
    if r.status_code != 200:
        raise Exception("Failed to get token")

    access_token = r.json()['access_token']
    return access_token

def requestJourney(location , destination):
    headers = {
        "Authorization": "Bearer {access_token}".format(access_token=WIMT_TOKEN),
        "Accept" : "application/json",
        "Content-Type" : "application/json"
    }
    body = {
        "geometry": {
            "type": "Multipoint",
            "coordinates": [location,destination]
        }
    }

    r = requests.post("{ROOT}/journeys".format(ROOT=PLATFORM_API_URL), data=body, headers=headers)
    journey = json.loads(r.text)

    print(journey)

    return journey

def getLine(location, destination):
    journey = requestJourney(location, destination)
    itineraries = journey['itineraries']
    for it in itineraries:
        legs = it['legs']
        for l in legs:
            if l['type'] == 'Transit':
                if l['line']['mode'] == 'ShareTaxi':
                    return l
    return "no line"    

def parseRoute(line):
    route = {}
    route['id'] = line['line']['id']
    route['name'] = line['line']['shortName']
    route['coordinates'] = []
    coords = line['geometry']['coordinates']
    for c in coords:
        route['coordinates'].append({'longitude': c[0],'latitude': c[1]})

    return json.dumps(route)

if __name__ == "__main__":
    WIMT_TOKEN = getAccessToken()
    line = getLine([18.676517,-34.030118],[18.566178,-33.979593])
    #print(line['line']['shortName'])
    #print(line['line']['id'])
    routeJson = parseRoute(line)
    #print(routeJson)

#[18.676517,-34.030118],[18.566178,-33.979593]
#[18.531295,-33.943695],[18.676517,-34.030118]
#[18.395448,-33.909531],[18.416798,-33.912683]