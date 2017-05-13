import datetime
import requests

CLIENT_ID = 'e562c31c-8d56-4696-858c-9331c21688d4'
CLIENT_SECRET = 'mYvtKREFRbA4zANzs1NQuGvLQmgOhmvJDpEl6kiu/cQ='
PLATFORM_API_URL = 'https://platform.whereismytransport.com/api'

TOKEN = ''

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

def requestJourney():
	headers = {
		"Authorization": "Bearer {access_token}".format(access_token=TOKEN),
		"Accept" : "application/json",
		"Content-Type" : "application/json"
	}
	body = {
		"geometry": {
			"type": "Multipoint",
			"coordinates": [
				[ 18.395448, -33.909531 ],
				[ 18.416798, -33.912683 ]
			]
		}
	}

	r = requests.post("{ROOT}/journeys".format(ROOT=PLATFORM_API_URL), data=body, headers=headers)
	journey = r.json()

	print(journey)

TOKEN = getAccessToken()
requestJourney()
